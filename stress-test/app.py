import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from module import run_benchmark

app = FastAPI()

BACKEND_API_SECRET_KEY=os.getenv("BACKEND_API_SECRET_KEY")


@app.post("/stress-test")
def stress_test(data: dict,
                credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    token_bearer = credentials.credentials
    if str(token_bearer) != BACKEND_API_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized request")

    run_benchmark(
        int(data["total_requests"]),
        int(data["concurrency_level"])
    )

    return {"status": 200}