import requests

# This points to your running FastAPI server
FASTAPI_BASE_URL = "http://127.0.0.1:8000/api/v1"

def submit_citizen_problem(payload: dict) -> dict:
    """Sends the citizen report to the FastAPI backend."""
    response = requests.post(f"{FASTAPI_BASE_URL}/submissions", json=payload)

    # Raise an error if FastAPI returns a 4xx or 5xx code
    response.raise_for_status()

    return response.json()