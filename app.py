import os
import json
import sqlite3
from flask import Flask, request, jsonify, render_template, g
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = Flask(__name__)

# --- CONFIG ---
WINDOW_SIZE = 10 
SUMMARIZER_MODEL = "llama-3.1-8b-instant" 
MAIN_MODEL = "llama-3.3-70b-versatile"

PATIENT_BEHAVIOR_DIRECTIVE = """
BEHAVIOR: Short, natural sentences. No asterisks. Do not info-dump. Stay in character.
"""

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("osce_platform.db")
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

def summarize_history(old_messages):
    try:
        formatted = "\n".join([f"{m['role']}: {m['content']}" for m in old_messages])
        prompt = f"Summarize clinical facts gathered: {formatted}"
        completion = client.chat.completions.create(
            model=SUMMARIZER_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"❌ Summarization Error: {e}")
        return "History follows."

@app.route("/")
def index():
    db = get_db()
    scenarios = db.execute("SELECT id, name FROM scenarios").fetchall()
    return render_template("index.html", scenarios=[dict(s) for s in scenarios])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    scenario_id = data.get("scenario_id")
    history = data.get("history", [])
    
    db = get_db()
    scenario = db.execute("SELECT patient_prompt FROM scenarios WHERE id =?", (scenario_id,)).fetchone()
    
    if not scenario:
        return jsonify({"error": "Scenario not found"}), 404

    sys_msg = f"{scenario['patient_prompt']}\n\n{PATIENT_BEHAVIOR_DIRECTIVE}"
    
    if len(history) > WINDOW_SIZE:
        summary = summarize_history(history[:-WINDOW_SIZE])
        messages = [{"role": "system", "content": f"{sys_msg}\n\nSummary: {summary}"}] + history[-WINDOW_SIZE:]
    else:
        messages = [{"role": "system", "content": sys_msg}] + history
    
    try:
        comp = client.chat.completions.create(model=MAIN_MODEL, messages=messages)
        return jsonify({"role": "assistant", "content": comp.choices[0].message.content})
    except Exception as e:
        print(f"❌ Chat API Error: {e}")
        return jsonify({"role": "assistant", "content": "I'm feeling a bit unwell..."}), 500

@app.route("/get_viva", methods=["POST"])
def get_viva():
    data = request.json
    db = get_db()
    scenario = db.execute("SELECT viva_questions FROM scenarios WHERE id =?", (data.get('scenario_id'),)).fetchone()
    if not scenario:
        return jsonify({"questions": []}), 404
    return jsonify({"questions": json.loads(scenario['viva_questions'])})

@app.route("/grade", methods=["POST"])
def grade():
    data = request.json
    db = get_db()
    scenario = db.execute("SELECT rubric FROM scenarios WHERE id =?", (data.get('scenario_id'),)).fetchone()
    
    transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in data.get('history', [])])
    original_rubric = json.loads(scenario['rubric'])
    item_names = [i['item'] for i in original_rubric]

    prompt = f"Grade this transcript against: {json.dumps(item_names)}. Return JSON: {{\"items\": [{{ \"item\": \"name\", \"completed\": true/false }}], \"feedback\": \"str\"}}"
    
    try:
        comp = client.chat.completions.create(
            model=MAIN_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(comp.choices[0].message.content)
        ai_map = {i['item']: i.get('completed', False) for i in result.get('items', [])}
        
        final_items = []
        for orig in original_rubric:
            final_items.append({"item": orig['item'], "completed": ai_map.get(orig['item'], False), "points": 1})

        earned = sum(1 for i in final_items if i['completed'])
        score = int((earned / len(final_items)) * 100)
        
        return jsonify({"score": score, "items": final_items, "feedback": result.get('feedback', "")})
    except Exception as e:
        print(f"❌ Grading Error: {e}")
        return jsonify({"error": "Failed", "score": 0}), 500

@app.route("/grade_viva", methods=["POST"])
def grade_viva():
    data = request.json 
    db = get_db()
    scenario = db.execute("SELECT viva_questions FROM scenarios WHERE id =?", (data.get('scenario_id'),)).fetchone()
    
    prompt = f"Grade these viva answers: {json.dumps(data.get('responses'))} against models: {scenario['viva_questions']}. Return JSON: {{\"score\": int, \"feedback\": \"str\"}}"
    
    try:
        comp = client.chat.completions.create(
            model=MAIN_MODEL, 
            messages=[{"role": "user", "content": prompt}], 
            response_format={"type": "json_object"}
        )
        return jsonify(json.loads(comp.choices[0].message.content))
    except Exception as e:
        print(f"❌ Viva Error: {e}")
        return jsonify({"score": 0, "feedback": "Failed"}), 500

@app.route("/final_assessment", methods=["POST"])
def final_assessment():
    data = request.json 
    final_score = (data.get('h_score', 0) * 0.4) + (data.get('v_score', 0) * 0.6)
    grade = "PASS" if final_score >= 60 else "FAIL"
    color = "#7c4dff" if grade == "PASS" else "#ff5252"
    return jsonify({"score": int(final_score), "grade": grade, "color": color})

if __name__ == "__main__":
    app.run(debug=True, port=5000)