import sqlite3
import json

def setup_database():
    db_name = "osce_platform.db"
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS scenarios")
    cursor.execute('''CREATE TABLE scenarios 
                      (id TEXT PRIMARY KEY, 
                       name TEXT, 
                       patient_prompt TEXT, 
                       rubric TEXT, 
                       viva_questions TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS attempts 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       student_name TEXT, 
                       score INTEGER, 
                       feedback TEXT, 
                       transcript TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    chest_pain_rubric = [
        {"category": "Opening", "item": "Introduces themselves", "completed": False, "points": 1},
        {"category": "Opening", "item": "Confirms patient details", "completed": False, "points": 1},
        {"category": "Opening", "item": "Establishes presenting complaint using open questioning", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES assessment", "completed": False, "points": 1},
        {"category": "HPC", "item": "Asks if patient experienced this previously", "completed": False, "points": 1},
        {"category": "HPC", "item": "Elicits ICE", "completed": False, "points": 1},
        {"category": "PMH", "item": "HTN / Lipids / Diabetes", "completed": False, "points": 1},
        {"category": "PMH", "item": "Previous CVD", "completed": False, "points": 1},
        {"category": "DH", "item": "Medications and ALLERGIES", "completed": False, "points": 1},
        {"category": "FH", "item": "Family history of CVD", "completed": False, "points": 1},
        {"category": "SH", "item": "Smoking / Alcohol / Occupation", "completed": False, "points": 1},
        {"category": "Communication", "item": "Active listening", "completed": False, "points": 1}
    ]

    abdominal_pain_rubric = [
        {"category": "Opening", "item": "Introduces and confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES assessment", "completed": False, "points": 1},
        {"category": "HPC", "item": "Radiation to right shoulder", "completed": False, "points": 1},
        {"category": "HPC", "item": "Association with fatty meals", "completed": False, "points": 1},
        {"category": "Systemic", "item": "Screens for Jaundice", "completed": False, "points": 1},
        {"category": "Systemic", "item": "Screens for Fever/Rigors", "completed": False, "points": 1},
        {"category": "PMH", "item": "Gallstones or abdominal surgeries", "completed": False, "points": 1},
        {"category": "DH", "item": "Medications and Allergies", "completed": False, "points": 1},
        {"category": "SH", "item": "Alcohol and Diet", "completed": False, "points": 1},
        {"category": "ICE", "item": "Elicits ICE", "completed": False, "points": 1},
        {"category": "Closing", "item": "Summarises findings", "completed": False, "points": 1}
    ]

    back_pain_rubric = [
        {"category": "Opening", "item": "Introduces and confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES assessment", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Saddle Anaesthesia", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bladder dysfunction", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bowel dysfunction", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bilateral Leg weakness", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Weight loss or Night pain", "completed": False, "points": 1},
        {"category": "PMH", "item": "History of Cancer or Trauma", "completed": False, "points": 1},
        {"category": "DH", "item": "Analgesia and Anticoagulants", "completed": False, "points": 1},
        {"category": "ICE", "item": "Elicits ICE", "completed": False, "points": 1}
    ]

    chest_pain_viva = [
        {"q": "What are your top three differentials?", "model": "ACS, PE, Aortic Dissection"},
        {"q": "Immediate management for ACS?", "model": "Aspirin 300mg, GTN, Morphine"},
        {"q": "ECG timeframe?", "model": "Within 10 mins"}
    ]

    abdominal_pain_viva = [
        {"q": "Primary diagnosis?", "model": "Acute Cholecystitis"},
        {"q": "Which physical sign confirms suspicion?", "model": "Murphy's Sign"},
        {"q": "Gold-standard initial imaging?", "model": "RUQ Ultrasound"}
    ]

    back_pain_viva = [
        {"q": "Most serious neuro emergency to rule out?", "model": "Cauda Equina Syndrome"},
        {"q": "Gold-standard investigation and timeframe?", "model": "MRI Spine within 4-6 hours"},
        {"q": "Definitive management if confirmed?", "model": "Emergency surgical decompression"}
    ]

    scenarios = [
        ('chest_pain', 'Chest Pain', 'You are Mr. Jones, 65, crushing chest pain.', json.dumps(chest_pain_rubric), json.dumps(chest_pain_viva)),
        ('abdominal_pain', 'Abdominal Pain', 'You are Mrs. Smith, 40, sharp RUQ pain.', json.dumps(abdominal_pain_rubric), json.dumps(abdominal_pain_viva)),
        ('back_pain', 'Back Pain', 'You are Mr. Taylor, 30, lower back pain.', json.dumps(back_pain_rubric), json.dumps(back_pain_viva))
    ]

    cursor.executemany("INSERT INTO scenarios VALUES (?,?,?,?,?)", scenarios)
    conn.commit()
    conn.close()
    print("✅ Database Synchronized.")

if __name__ == "__main__":
    setup_database()