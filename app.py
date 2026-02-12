import os, json, sqlite3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
app = Flask(__name__)

# --- CONFIG ---
WINDOW_SIZE = 10 
SUMMARIZER_MODEL = "llama-3-8b-8192"
MAIN_MODEL = "llama-3.3-70b-versatile"

PATIENT_BEHAVIOR_DIRECTIVE = """
BEHAVIOR RULES:
1. Speak in short, natural conversational sentences. 
2. DO NOT use asterisks or describe actions (e.g., no *coughs*).
3. Do not info-dump; wait for questions.
4. Stay in character.
"""

def get_db_connection():
    conn = sqlite3.connect("osce_platform.db")
    conn.row_factory = sqlite3.Row
    return conn

def summarize_history(old_messages):
    try:
        formatted = "\n".join([f"{m['role']}: {m['content']}" for m in old_messages])
        prompt = f"Summarize clinical facts: {formatted}"
        completion = client.chat.completions.create(
            model=SUMMARIZER_MODEL,
            messages=[{"role": "system", "content": "Scribe."}, {"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except: return "History follows."

@app.route("/")
def index():
    conn = get_db_connection()
    scenarios = conn.execute("SELECT id, name FROM scenarios").fetchall()
    conn.close()
    return render_template("index.html", scenarios=[dict(s) for s in scenarios])

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    scenario_id = data.get("scenario_id")
    history = data.get("history", [])
    conn = get_db_connection()
    scenario = conn.execute("SELECT patient_prompt FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
    conn.close()

    sys_msg = f"{scenario['patient_prompt']}\n\n{PATIENT_BEHAVIOR_DIRECTIVE}"
    if len(history) > WINDOW_SIZE:
        summary = summarize_history(history[:-WINDOW_SIZE])
        messages = [{"role": "system", "content": f"{sys_msg}\nSummary: {summary}"}] + history[-WINDOW_SIZE:]
    else:
        messages = [{"role": "system", "content": sys_msg}] + history
    
    comp = client.chat.completions.create(model=MAIN_MODEL, messages=messages)
    return jsonify({"role": "assistant", "content": comp.choices[0].message.content})

@app.route("/grade", methods=["POST"])
def grade():
    data = request.json
    scenario_id = data.get("scenario_id")
    history = data.get("history", [])

    conn = get_db_connection()
    scenario = conn.execute("SELECT rubric, name FROM scenarios WHERE id = ?", (scenario_id,)).fetchone()
    
    transcript = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in history])
    original_rubric = json.loads(scenario['rubric'])
    item_names = [i['item'] for i in original_rubric]

    prompt = f"Grade strictly on these items: {json.dumps(item_names)}. Return JSON with 'items' (list of {{item:str, completed:bool}}), 'score' (int), and 'feedback' (3 sentences)."
    
    try:
        comp = client.chat.completions.create(
            model=MAIN_MODEL,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": transcript}],
            response_format={"type": "json_object"}
        )
        result = json.loads(comp.choices[0].message.content)
        
        # Match items to calculate score accurately
        ai_map = {i['item']: i['completed'] for i in result.get('items', [])}
        final_items = []
        for orig in original_rubric:
            final_items.append({
                "item": orig['item'],
                "completed": ai_map.get(orig['item'], False),
                "points": orig.get('points', 1)
            })

        score = int((sum(i['points'] for i in final_items if i['completed']) / sum(i['points'] for i in final_items)) * 100)
        feedback = result.get('feedback', "See checklist.")

        # --- DB SAVE (Wrapped in Try to prevent UI crash) ---
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO attempts (student_name, score, feedback, transcript) VALUES (?,?,?,?)",
                           ("Student", score, feedback, transcript))
            conn.commit()
        except Exception as db_err:
            print(f"DB Insert Failed: {db_err}")
        finally:
            conn.close()

        return jsonify({"score": score, "items": final_items, "feedback": feedback})
    except Exception as e:
        print(f"Grading Error: {e}")
        return jsonify({"error": "Failed to grade"}), 500

if __name__ == "__main__":
    app.run(debug=True)