import io
import os
import re
import jwt
import json
import pytz
import psycopg2
import warnings
import numpy as np
import pandas as pd
from google import genai
from datetime import datetime
from google.genai import types
from template_prompt import template_statement_extractor, template_prompt_new


QUERY_PATH="./queries"
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")


def postgresql_connect():
    """
    Connect postgresql
    """
    database_client = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    return database_client


def decode_jwt(token: str) -> dict:
    """
    Decode JWT token
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def insert_log_data(json_data: dict,
                    token_data: dict,
                    email: str):
    """
    Insert log data after processing document
    """
    connection = postgresql_connect()
    cursor = connection.cursor()

    with open(f"{QUERY_PATH}/insert_log_data.sql", "r") as openfile:
        query_file = openfile.read()
    values = (
        str(email), # For lookup id
        str(email), # For insert email
        json.dumps(json_data),
        token_data["input_token"],
        token_data["output_token"],
        datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query_file, values)
    connection.commit()
    connection.close()


def get_log_data(email: str):
    """
    Get log data
    """
    connection = postgresql_connect()
    with open(f"{QUERY_PATH}/get_log_data.sql", "r") as openfile:
        query_file = openfile.read()
    query_file = query_file.replace("@email", str(email))

    df_log = pd.read_sql_query(query_file, connection)
    connection.close()

    return df_log


def statement_extractor(input_file: bytes,
                        email: str):
    """
    Extract information within document
    """
    # Define the google client service
    client = genai.Client(api_key=os.getenv("GOOGLE_CLOUD_API_KEY"))

    # Get response from gemini model
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=[
            types.Part.from_bytes(
                data=input_file,
                mime_type="image/jpeg"
            ),
            template_prompt_new
        ]
    )

    string_response = re.sub(r"\n", "", str(response.text))
    json_data = json.loads(re.findall(r"\{.*\}", string_response)[0])
    if not json_data:
        json_data = {
            "transaction_details": {}
        }
    else:
        for table in json_data.keys():  # Get every table's name
            # Check the length of every column's value on each table
            list_length = [
                len(json_data[table][element]) for element in json_data[table].keys()
            ]
            # Handle if there are inconsistent list length in every table values
            if len(list(set(list_length))) > 1:
                max_length = max(list_length)  # Get max length among all columns in each table
                for column in json_data[table].keys():  # Get column's name
                    if len(json_data[table][column]) < max_length:
                        length_missing_values = max_length - len(json_data[table][column])
                        json_data[table][column] += np.repeat("", length_missing_values).tolist()

        # Convert json data from dictionary to list format for front-end format
        # Convert to dataframe first for easier mapping to dictionary format
        final_data = {}
        list_table = [table for table in json_data.keys()]
        for table in list_table:
            df = pd.DataFrame(json_data[table])
            # Convert into dictionary with records orientation
            final_data[table] = df.to_dict(orient="records")


        json_data = {
            "transaction_details": final_data
        }
        token_data = {
            "input_token": response.usage_metadata.prompt_token_count,
            "output_token": response.usage_metadata.candidates_token_count
        }
        # Insert log data to database
        insert_log_data(json_data, token_data, email)


    return json_data


def construct_extraction_file(email: str):
    """
    If user clicks the download XLSX button, this will construct
    LLM response into dataframe
    """
    warnings.filterwarnings("ignore")
    df_log = get_log_data(email)

    json_data = df_log["log_data"].values[0]
    transactions_detail = json_data["transaction_details"]

    list_tables = transactions_detail.keys()
    output_file_on_memory = io.BytesIO()
    with pd.ExcelWriter(output_file_on_memory) as writer:
        for table in list_tables:
            df = pd.DataFrame(transactions_detail[table])
            df.to_excel(writer, sheet_name=table, index=False)
    output_file_on_memory.seek(0)

    return output_file_on_memory