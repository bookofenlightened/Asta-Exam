from flask import Flask, render_template, request, jsonify
import os, time
from werkzeug.utils import secure_filename
from utils.pdf_extract import extract_text
from utils.ai_generate import generate_questions
from db_utils import get_conn

# Auto-create table on startup
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id SERIAL PRIMARY KEY,
        question_text TEXT,
        option_a TEXT,
        option_b TEXT,
        option_c TEXT,
        option_d TEXT,
        correct_answer TEXT,
        difficulty VARCHAR(20),
        source VARCHAR(50),
        approved BOOLEAN DEFAULT FALSE,
        source_pdf TEXT
    );
    """)
    conn.commit()
    conn.close()

init_db()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET','POST'])
def upload():
    if request.method == 'POST':
        file = request.files['pdf']
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_DIR, f"{int(time.time())}_{filename}")
        file.save(path)

        # Extract text
        text = extract_text(path)
        if not text.strip():
            return "No text extracted", 400

        # Generate questions from AI
        questions = generate_questions(text)

        # Insert into DB
        conn = get_conn()
        cursor = conn.cursor()
        ins = """INSERT INTO questions 
                 (question_text, option_a, option_b, option_c, option_d, correct_answer, difficulty, source, approved, source_pdf) 
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        for q in questions:
            opts = q.get('options', {})
            vals = (q.get('question'), opts.get('A'), opts.get('B'), opts.get('C'), opts.get('D'),
                    q.get('answer'), q.get('difficulty','Medium'), "AI", True, path)
            try:
                cursor.execute(ins, vals)
            except Exception as e:
                print("DB insert error:", e)
        conn.commit()
        conn.close()

        return jsonify({"ok": True, "inserted": len(questions)})
    return render_template('upload.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
