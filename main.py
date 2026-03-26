from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.aadhaar import extract_aadhaar
import uvicorn
import os

app = FastAPI(
    title="Aadhaar Extraction API",
    description="Extracts structured data from Aadhaar PDFs using the IntellectSee platform.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AadhaarRequest(BaseModel):
    pdf_base64: str  # Base64-encoded Aadhaar PDF


class AadhaarResponse(BaseModel):
    aadhaar_no: str
    name: str
    date_of_birth: str
    gender: str
    address: str


@app.get("/")
def health_check():
    return {"status": "ok", "message": "Aadhaar Extraction API is running."}


@app.post("/extract", response_model=AadhaarResponse)
def extract(request: AadhaarRequest):
    """
    Accepts a base64-encoded Aadhaar PDF and returns extracted details.
    """
    try:
        result = extract_aadhaar(request.pdf_base64)
        return AadhaarResponse(
            aadhaar_no=result["Aadhaar No"],
            name=result["Name"],
            date_of_birth=result["Date of Birth"],
            gender=result["Gender"],
            address=result["Address"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
