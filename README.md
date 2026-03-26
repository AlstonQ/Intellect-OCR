# Aadhaar Extraction API

A FastAPI service that extracts structured data from Aadhaar PDFs using the IntellectSee MagicPlatform.

## Endpoints

### `GET /`
Health check.

### `POST /extract`
Extracts Aadhaar details from a base64-encoded PDF.

**Request Body:**
```json
{
  "pdf_base64": "<base64-encoded PDF string>"
}
```

**Response:**
```json
{
  "aadhaar_no": "XXXXXXXX5361",
  "name": "Palak Ramesh Lalwani",
  "date_of_birth": "04/04/2004",
  "gender": "FEMALE",
  "address": "D/O: Ramesh Lalwani, ..."
}
```

---

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/aadhaar-api.git
cd aadhaar-api

cp .env.example .env
# Edit .env with your credentials

pip install -r requirements.txt
python main.py
```

API will be live at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

---

## Deploy on Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → **New Project** → **Deploy from GitHub repo**
3. Select this repo
4. Go to **Variables** tab and add all keys from `.env.example`
5. Railway auto-deploys — your API URL will be shown in the dashboard

---

## Convert PDF to Base64 (Quick Snippet)

```python
import base64

with open("aadhaar.pdf", "rb") as f:
    pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

print(pdf_base64)
```
