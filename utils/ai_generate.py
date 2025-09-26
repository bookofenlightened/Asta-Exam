import os, requests, json
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={API_KEY}"

def generate_questions(text):
    prompt = f"""
    Generate 5 admission test style MCQs from the following text.
    Return JSON array with: question, options(A-D), answer, difficulty.
    Text:\n{text}
    """
    headers = {"Content-Type": "application/json"}
    body = {"contents":[{"parts":[{"text":prompt}]}]}
    res = requests.post(API_URL, headers=headers, json=body)
    data = res.json()
    try:
        output = data['candidates'][0]['content']['parts'][0]['text']
        return json.loads(output)
    except Exception as e:
        print("AI parse error:", e)
        return []
