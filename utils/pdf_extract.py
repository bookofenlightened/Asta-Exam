import pdfplumber, requests, os
from dotenv import load_dotenv
load_dotenv()

OCR_KEY = os.getenv("OCR_API_KEY")
OCR_URL = "https://api.ocr.space/parse/image"

def extract_text(path):
    text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        print("pdfplumber error:", e)

    if not text.strip():
        # fallback OCR
        with open(path, 'rb') as f:
            res = requests.post(OCR_URL, files={"file": f}, data={"apikey": OCR_KEY, "language": "eng"})
        rj = res.json()
        if rj.get("ParsedResults"):
            text = rj["ParsedResults"][0]["ParsedText"]
    return text
