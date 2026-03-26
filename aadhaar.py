import requests
import base64
import json
import time
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
# CONFIGURATION (from environment variables)
# ─────────────────────────────────────────
API_KEY       = os.environ.get("API_KEY", "magicplatform.c630A0A1126e4dA3A0D11218625d3331")
BASE_URL      = os.environ.get("BASE_URL", "https://api.intellectseecstag.com")
ASSET_ID      = os.environ.get("ASSET_ID", "54be83b5-1dba-4a8d-b616-93555c462655")
USERNAME      = os.environ.get("API_USERNAME", "idxpdemo.demo.user")
PASSWORD      = os.environ.get("API_PASSWORD", "Chief@admin2025")
TENANT        = os.environ.get("TENANT", "idxpdemo")
POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 3))
MAX_RETRIES   = int(os.environ.get("MAX_RETRIES", 20))


# ─────────────────────────────────────────
# STEP 1 — AUTHENTICATE
# ─────────────────────────────────────────
def get_access_token() -> str:
    url = f"{BASE_URL}/accesstoken/{TENANT}"
    headers = {
        "apikey":   API_KEY,
        "username": USERNAME,
        "password": PASSWORD,
        "Accept":   "application/json"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    data = response.json()

    if data.get("result") != "RESULT_SUCCESS":
        raise Exception(f"Authentication failed: {data}")

    return data["access_token"]


# ─────────────────────────────────────────
# STEP 2 — SUBMIT PDF & GET TRACE ID
# ─────────────────────────────────────────
def submit_pdf(access_token: str, pdf_base64: str) -> str:
    url = f"{BASE_URL}/magicplatform/v1/invokeasset/{ASSET_ID}/genai?add_additional_model_output=false"
    headers = {
        "apikey":        API_KEY,
        "Accept":        "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    pdf_bytes = base64.b64decode(pdf_base64)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            files = [("aadhaar", ("aadhaar.pdf", f, "application/pdf"))]
            response = requests.post(url, headers=headers, files=files, timeout=60)
        response.raise_for_status()
    finally:
        os.remove(tmp_path)

    data = response.json()
    trace_id = data.get("trace_id")

    if not trace_id:
        raise Exception(f"No trace_id returned: {data}")

    return trace_id


# ─────────────────────────────────────────
# STEP 3 — POLL UNTIL COMPLETED
# ─────────────────────────────────────────
def poll_result(access_token: str, trace_id: str) -> dict:
    url = f"{BASE_URL}/magicplatform/v1/invokeasset/{ASSET_ID}/{trace_id}"
    headers = {
        "apikey":        API_KEY,
        "Accept":        "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    for attempt in range(1, MAX_RETRIES + 1):
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        status = data.get("status", "")

        if status == "COMPLETED":
            return data
        if status == "FAILED":
            raise Exception(f"Processing failed on attempt {attempt}: {data}")

        time.sleep(POLL_INTERVAL)

    raise Exception(f"Timed out after {MAX_RETRIES} attempts. Processing not completed.")


# ─────────────────────────────────────────
# PARSE OUTPUT
# ─────────────────────────────────────────
def parse_output(result: dict) -> dict:
    raw = result.get("response", {}).get("output", {}).get("autogen_results", "")
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    extracted = json.loads(clean)

    return {
        "Aadhaar No":    extracted.get("aadhaar_number", "N/A"),
        "Name":          extracted.get("name", "N/A"),
        "Date of Birth": extracted.get("dob", "N/A"),
        "Gender":        extracted.get("gender", "N/A"),
        "Address":       extracted.get("address", "N/A")
    }


# ─────────────────────────────────────────
# MAIN PIPELINE
# ─────────────────────────────────────────
def extract_aadhaar(pdf_base64: str) -> dict:
    access_token = get_access_token()
    trace_id     = submit_pdf(access_token, pdf_base64)
    result       = poll_result(access_token, trace_id)
    return parse_output(result)
