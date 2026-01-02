import os
import json
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from module import (statement_extractor,
                    construct_extraction_file)


BACKEND_API_SECRET_KEY=os.getenv("BACKEND_API_SECRET_KEY")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("WEBSITE_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

thread_executors = ThreadPoolExecutor(
    max_workers=int(os.getenv("THREAD_NUMBERS"))
)



@app.post("/download-xlsx")
async def download_xlsx(data: dict = Body(...),
                        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    This is API endpoint to download XLSX file after processing extraction
    """
    async_loop = asyncio.get_running_loop()

    token_bearer = credentials.credentials
    if str(token_bearer) != BACKEND_API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized request")
    
    try:
        buffer = await async_loop.run_in_executor(thread_executors, construct_extraction_file, data["email"])

        return StreamingResponse(
            buffer
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to process XLSX file")


@app.post("/statement-extractor")
async def process_statement(file_byte: UploadFile = File(...),
                            additional_data: str = Form(...),
                            credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """
    This is the endpoint to extract information within uploaded document
    """
    async_loop = asyncio.get_running_loop()

    token_bearer = credentials.credentials
    if str(token_bearer) != BACKEND_API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized request")

    try:
        # Unpack body email data
        file_byte = await file_byte.read()
        additional_data_json = json.loads(additional_data)

        # Check available balance to run the service
        if additional_data_json["remaining_balance"] == 0:
            raise HTTPException(status_code=402, detail="Insufficient balance")

        output_data = await async_loop.run_in_executor(thread_executors, statement_extractor, file_byte, additional_data_json["email"])

        json_output = {
            "data": output_data
        }

        return json_output
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to extract information within the document")