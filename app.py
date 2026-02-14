import os
import json
import sqlite3
import datetime
from flask import Flask, request, jsonify, render_template, g
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = Flask(__name__)

# --- CONFIG ---
WINDOW_SIZE = 15 
SUMMARIZER_MODEL = "llama-3.1-8b-instant" 
MAIN_MODEL = "llama-3.3-70b-versatile"

PATIENT_BEHAVIOR_DIRECTIVE = """
SYSTEM INSTRUCTION: You are a simulated patient in a medical OSCE exam. 
1. React naturally to the student's questions. 
2. Do NOT volunteer information unless asked (unless the scenario says you are very anxious/talkative).
3. If the student is empathetic, respond well. If they are rude, become closed off.
4. Keep responses concise (under 3 sentences) to allow for back-and-forth dialogue.
5. NO formatting (no bolding, no bullet points). Speak like a human.
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
        prompt = f"Summarize the clinical facts gathered so far in this conversation. Keep it strictly factual:\n\n{formatted}"
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
    # Get scenarios
    scenarios = db.execute("SELECT id, name FROM scenarios").fetchall()
    # Get previous attempts for a mini dashboard (optional, but good for verification)
    attempts = db.execute("SELECT student_name, score, timestamp FROM attempts ORDER BY id DESC LIMIT 5").fetchall()
    return render_template("index.html", scenarios=[dict(s) for s in scenarios], attempts=[dict(a) for a in attempts])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    scenario_id = data.get("scenario_id")
    history = data.get("history", [])
    
    db = get_db()
    scenario = db.execute("SELECT patient_prompt FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
    
    if not scenario:
        return jsonify({"error": "Scenario not found"}), 404

    sys_msg = f"{scenario['patient_prompt']}\n\n{PATIENT_BEHAVIOR_DIRECTIVE}"
    
    if len(history) > WINDOW_SIZE:
        summary = summarize_history(history[:-WINDOW_SIZE])
        messages = [{"role": "system", "content": f"{sys_msg}\n\nCONTEXT SUMMARY: {summary}"}] + history[-WINDOW_SIZE:]
    else:
        messages = [{"role": "system", "content": sys_msg}] + history
    
    try:
        comp = client.chat.completions.create(model=MAIN_MODEL, messages=messages, temperature=0.7)
        return jsonify({"role": "assistant", "content": comp.choices[0].message.content})
    except Exception as e:
        print(f"❌ Chat API Error: {e}")
        return jsonify({"role": "assistant", "content": "I'm feeling a bit faint... (System Error)"}), 500

@app.route("/get_viva", methods=["POST"])
def get_viva():
    data = request.json
    db = get_db()
    scenario = db.execute("SELECT viva_questions FROM scenarios WHERE id = ?", (data.get('scenario_id'),)).fetchone()
    if not scenario:
        return jsonify({"questions": []}), 404
    return jsonify({"questions": json.loads(scenario['viva_questions'])})

@app.route("/grade", methods=["POST"])
def grade():
    data = request.json
    db = get_db()
    scenario = db.execute("SELECT rubric FROM scenarios WHERE id = ?", (data.get('scenario_id'),)).fetchone()
    
    transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in data.get('history', [])])
    original_rubric = json.loads(scenario['rubric'])
    item_names = [i['item'] for i in original_rubric]

    prompt = f"""
    You are a strict medical examiner. Grade this student-patient transcript.
    
    TRANSCRIPT:
    {transcript}
    
    CHECKLIST ITEMS TO FIND:
    {json.dumps(item_names)}
    
    Return ONLY a JSON object: 
    {{ "items": [{{ "item": "exact_item_name_from_list", "completed": true/false }}], "feedback": "Brief constructive feedback for the student (max 50 words)." }}
    """
    
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
            is_done = ai_map.get(orig['item'], False)
            final_items.append({
                "category": orig['category'],
                "item": orig['item'], 
                "completed": is_done, 
                "points": orig['points'] if is_done else 0,
                "max_points": orig['points']
            })

        earned_points = sum(i['points'] for i in final_items)
        total_points = sum(i['max_points'] for i in final_items)
        score = int((earned_points / total_points) * 100) if total_points > 0 else 0
        
        return jsonify({"score": score, "items": final_items, "feedback": result.get('feedback', "")})
    except Exception as e:
        print(f"❌ Grading Error: {e}")
        return jsonify({"error": "Failed", "score": 0}), 500

@app.route("/grade_viva", methods=["POST"])
def grade_viva():
    data = request.json 
    db = get_db()
    scenario = db.execute("SELECT viva_questions FROM scenarios WHERE id = ?", (data.get('scenario_id'),)).fetchone()
    
    prompt = f"""
    Grade these medical viva answers. Be fair but accurate.
    
    QUESTIONS & MODEL ANSWERS:
    {scenario['viva_questions']}
    
    STUDENT ANSWERS:
    {json.dumps(data.get('responses'))}
    
    Return ONLY a JSON object:
    {{ "score": integer_0_to_100, "feedback": "Brief feedback on knowledge gaps." }}
    """
    
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
    
    # Calculate Final Grade
    final_score = (data.get('h_score', 0) * 0.5) + (data.get('v_score', 0) * 0.5)
    final_score = int(final_score)
    
    grade = "PASS" if final_score >= 60 else "FAIL"
    color = "#34C759" if grade == "PASS" else "#FF3B30" # Apple Green / Apple Red
    
    # Compile Transcript for DB
    full_transcript = "--- HISTORY ---\n"
    for msg in data.get('history', []):
        full_transcript += f"{msg['role'].upper()}: {msg['content']}\n"
    
    full_transcript += "\n--- VIVA ---\n"
    viva_responses = data.get('viva_responses', [])
    for idx, resp in enumerate(viva_responses):
        full_transcript += f"Q{idx+1}: {resp}\n"

    # Compile Combined Feedback
    combined_feedback = f"HISTORY: {data.get('h_feedback', '')} | VIVA: {data.get('v_feedback', '')}"

    # --- THE DB FIX: INSERTING DATA ---
    try:
        db = get_db()
        db.execute(
            "INSERT INTO attempts (student_name, score, feedback, transcript) VALUES (?, ?, ?, ?)",
            ("Student", final_score, combined_feedback, full_transcript)
        )
        db.commit()
        print(f"✅ Attempt saved for scenario {data.get('scenario_id')} with score {final_score}")
    except Exception as e:
        print(f"❌ Database Save Error: {e}")
        # We proceed anyway to show the user their grade even if DB fails

    return jsonify({"score": final_score, "grade": grade, "color": color})

if __name__ == "__main__":
    app.run(debug=True, port=5000)