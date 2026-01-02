import os
import json
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from module import run_benchmark

app = FastAPI()

BACKEND_API_SECRET_KEY=os.getenv("BACKEND_API_SECRET_KEY")


@app.post("/stress-test")
def stress_test(file_byte: UploadFile = File(...),
                request_config: str = Form(...),
                credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token_bearer = credentials.credentials
    if str(token_bearer) != BACKEND_API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized request")

    file_byte = file_byte.read()
    additional_data_json = json.loads(request_config)

    run_benchmark(
        file_byte,
        int(additional_data_json["total_requests"]),
        int(additional_data_json["concurrency_level"])
    )

    return {"status": 200}