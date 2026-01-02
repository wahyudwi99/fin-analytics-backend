import os
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import statistics
import json

URL = "https://extraction-endpoint.extplan.io/statement-extractor"


def send_request(file_byte,
                 request_id):
    additional_data = {
        "email": "wahyudwinugraha99@gmail.com",
        "remaining_balance": 900
    }

    files_data = {
        "file_byte": ("image.png", file_byte, "application/octet-stream"),
        "additional_data": (None, json.dumps(additional_data), "application/json")
    }

    header = {
        "Authorization": f"Bearer {os.getenv('BACKEND_API_SECRET_KEY')}"
    }
    
    start_time = time.perf_counter()
    try:
        response = requests.post(URL, files=files_data, headers=header, timeout=60)
        end_time = time.perf_counter()
        
        latency = end_time - start_time
        status = response.status_code
        
        return {
            "id": request_id,
            "latency": latency,
            "status": status,
            "success": status == 200
        }
    except Exception as e:
        return {
            "id": request_id,
            "latency": time.perf_counter() - start_time,
            "status": "Error",
            "success": False,
            "error_msg": str(e)
        }

def run_benchmark(file_byte: bytes,
                  total_requests: int,
                  concurrency_level: int):
    print(f"🚀 Start Stress Test: {total_requests} requests...")
    print(f"🔥 Concurrency: {concurrency_level} threads\n")
    
    overall_start = time.perf_counter()
    
    with ThreadPoolExecutor(max_workers=concurrency_level) as executor:
        results = list(executor.map(send_request, file_byte, range(total_requests)))
    
    overall_end = time.perf_counter()
    
    latencies = [r['latency'] for r in results if r['success']]
    errors = [r for r in results if not r['success']]
    
    total_time = overall_end - overall_start
    
    print("="*30)
    print("📊 STRESS TEST RESULT")
    print("="*30)
    print(f"Total Test Time          : {total_time:.2f} seconds")
    print(f"Success Requests         : {len(latencies)}/{total_requests}")
    print(f"Failed Requests          : {len(errors)}")
    
    if latencies:
        print(f"Average Latency         : {statistics.mean(latencies):.2f} seconds")
        print(f"Fastest Latency (Min)   : {min(latencies):.2f} seconds")
        print(f"Longest Latency (Max)   : {max(latencies):.2f} seconds")
        if len(latencies) > 1:
            print(f"Median Latency (P50)   : {statistics.median(latencies):.2f} seconds")
            latencies.sort()
            p95_index = int(0.95 * len(latencies))
            print(f"Latency P95            : {latencies[p95_index]:.2f} seconds")
    
    if errors:
        print("\n❌ ERROR DETAILS:")
        for err in errors[:5]:
            print(f"- ID {err['id']}: {err['status']} ({err.get('error_msg', 'N/A')})")