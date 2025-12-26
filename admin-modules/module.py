import os
import jwt
import pytz
import psycopg2
import requests
import warnings
import pandas as pd
from datetime import datetime, timedelta


# Define global variables
QUERY_DIR_PATH="./queries"
JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")


def postgresql_connect():
    """
    Connect to postgresql database
    """
    database_client = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
    )

    return database_client


def create_jwt(data: dict):
    """
    Create JWT token for cookie session
    """
    data["exp"] = datetime.utcnow() + timedelta(hours=4)
    token = jwt.encode(data, JWT_SECRET_KEY, JWT_ALGORITHM)

    return token


def decode_jwt(token: str):
    """
    Decode JWT token which is retrieved from client
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}
    

def insert_new_user(json_data):
    """
    Insert new user after signing up
    """
    connection = postgresql_connect()
    cursor = connection.cursor()

    created_at = datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d")

    with open("./queries/insert_new_user.sql", "r") as openfile:
        query_file = openfile.read()

    values = (
        json_data["name"],
        json_data["email"],
        json_data["address"],
        json_data["phone_number"],
        created_at
    )
    cursor.execute(query_file, values)
    connection.commit()

    cursor.close()
    connection.close()


def process_balance(df_billing, df_count_transactions):
    """
    Get remaining and expired balance date
    """
    billing_created_at = df_billing["created_at"].values[0].astype('M8[ms]').astype('O')
    # Calculate remaining balance
    total_transactions = df_count_transactions["total_log_data"].values[0] if df_count_transactions.values.tolist() else 0
    date_now_minus_billing_date = datetime.utcnow() - billing_created_at
    remaining_balance = int(df_billing["total_balance"].values[0] - total_transactions)
    if remaining_balance < 0 or (date_now_minus_billing_date.days > int(df_billing["balance_duration_days"].values[0])):
        remaining_balance = 0

    # Calculate expired balance
    billing_created_at = df_billing["created_at"].values[0].astype('M8[ms]').astype('O')
    expired_balance_date = billing_created_at + timedelta(days=int(df_billing["balance_duration_days"].values[0]))

    return remaining_balance, expired_balance_date


def get_user_payment(email: str):
    """
    Get payment made by users
    """
    warnings.filterwarnings("ignore")
    connection = postgresql_connect()
    # Get billing and transactions data
    with open(f"{QUERY_DIR_PATH}/get_user_payment.sql", "r") as openfile:
        query_file = openfile.read()
        query_file = query_file.replace("@user_email", email)
        df_payment = pd.read_sql_query(query_file, connection)
    if df_payment.values.tolist():
        payment_created_at = df_payment["created_at"].values[0]
        payment_created_at_str = payment_created_at.astype('M8[ms]').astype('O').strftime("%Y-%m-%d %H:%M:%S")
        # Get total transactions made by users
        with open(f"{QUERY_DIR_PATH}/get_count_transaction_log.sql") as openfile:
            query_file = openfile.read()
            query_file = query_file.replace("@payment_created_at", str(payment_created_at_str))
            df_count_transactions = pd.read_sql_query(query_file, connection)

    # Construct json response
    if df_payment.values.tolist():
        remaining_balance, expired_balance_date = process_balance(df_payment, df_count_transactions)
        user_billing_json = {
            "data": {
                "user_id": int(df_payment["user_id"].values[0]),
                "user_email": df_payment["user_email"].values[0],
                "amount": int(df_payment["amount"].values[0]),
                "total_balance": int(df_payment["total_balance"].values[0]),
                "plan": df_payment["plan"].values[0],
                "remaining_balance": remaining_balance,
                "expired_balance_date": expired_balance_date.strftime("%d %b %Y"),
                "created_at": df_payment["created_at"].values[0].astype('M8[ms]').astype('O').strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    else:
        user_billing_json = {
            "data": "data is not found !"
        }

    connection.close()

    return user_billing_json


def get_user_profile_data(email: str):
    """
    Process user profile data
    """
    warnings.filterwarnings("ignore")
    connection = postgresql_connect()

    # Get user profile data
    with open(f"{QUERY_DIR_PATH}/get_user_profile.sql", "r") as openfile:
        query_file = openfile.read()
        query_file = query_file.replace("@email", str(email))
        df_user_profile = pd.read_sql_query(query_file, connection)
    # Construct data
    if df_user_profile.values.tolist():
        updated_at = df_user_profile["updated_at"].values[0]
        if updated_at is not None:
            updated_at = updated_at.astype('M8[ms]').astype('O').strftime("%d %b %Y")
        created_at = df_user_profile["created_at"].values[0].astype('M8[ms]').astype('O').strftime("%d %b %Y")
        user_profile_json = {
            "data": {
                "id": int(df_user_profile["id"].values[0]),
                "name": df_user_profile["name"].values[0],
                "email": df_user_profile["email"].values[0],
                "address": df_user_profile["address"].values[0],
                "phone_number": df_user_profile["phone_number"].values[0],
                "last_updated_at": updated_at if updated_at is not None else created_at
            }
        }
    else:
        user_profile_json = {
            "data": "data is not found !"
        }


    connection.close()

    return user_profile_json


def update_user_profile_data(json_data):
    """
    Update user profile data if there is change on the client
    """
    # Get data
    name = json_data["name"]
    email = json_data["email"]
    address = json_data["address"]
    phone_number = json_data["phone_number"]

    connection = postgresql_connect()
    cursor = connection.cursor()

    with open(f"{QUERY_DIR_PATH}/update_user_profile.sql", "r") as openfile:
        query_file = openfile.read()
        query_file = query_file.replace('@name', str(name))
        query_file = query_file.replace('@email', str(email))
        query_file = query_file.replace('@address', str(address))
        query_file = query_file.replace('@phone_number', str(phone_number))
        query_file = query_file.replace('@updated_at', datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S"))

    cursor.execute(query_file)
    connection.commit()
    cursor.close()
    connection.close()

    print(f"Successfully updated user's data for {email} !!")


def insert_payment(payment_data: dict):
    """
    Insert payments
    """
    connection = postgresql_connect()
    cursor = connection.cursor()

    with open(f"{QUERY_DIR_PATH}/insert_payment.sql", "r") as openfile:
        query_file = openfile.read()

    values = (
        payment_data["user_id"],
        payment_data["user_email"],
        payment_data["amount"],
        payment_data["total_balance"],
        payment_data["balance_duration_days"],
        payment_data["plan"],
        payment_data["payment_status"],
        payment_data["payment_id"],
        datetime.now(pytz.timezone("UTC")).strftime("%Y-%m-%d %H:%M:%S")
    )
    cursor.execute(query_file, values)
    connection.commit()

    cursor.close()
    connection.close()

    print("Successfully inserted payment data !")


def get_in_progress_payment(user_email: str):
    warnings.filterwarnings("ignore")
    connection = postgresql_connect()
    with open(f"{QUERY_DIR_PATH}/get_in_progress_payment.sql", "r") as openfile:
        query_file = openfile.read()
        query_file = query_file.replace("@EMAIL", str(user_email))
    
    df = pd.read_sql_query(query_file, connection)
    if df.values.tolist():
        payment_token = df["payment_id"].values[0]
    else:
        payment_token = None

    connection.close()

    return payment_token



def update_payment(payment_id: str,
                   payment_status: str):
    connection = postgresql_connect()
    cursor = connection.cursor()

    with open(f"{QUERY_DIR_PATH}/update_payment.sql", "r") as openfile:
        query_file = openfile.read()
        query_file = query_file.replace("@PAYMENT_ID", str(payment_id))
        query_file = query_file.replace("@PAYMENT_STATUS", str(payment_status))
        query_file = query_file.replace("@UPDATED_AT", datetime.now(pytz.timezone('UTC')).strftime("%Y-%m-%d %H:%M:%S"))
    
    cursor.execute(query_file, connection)
    connection.commit()

    cursor.close()
    connection.close()


def get_paypal_access_token():
    warnings.filterwarnings("ignore")
    response = requests.post(
        url=f"{os.getenv('PAYPAL_BASE_URL')}/v1/oauth2/token",
        data={"grant_type": "client_credentials"},
        auth=(os.getenv("PAYPAL_CLIENT_ID"), os.getenv("PAYPAL_CLIENT_SECRET"))
    )
    if response.status_code == 200:
        access_token = response.json()["access_token"]
    else:
        access_token = None

    return access_token