import sqlite3
import json

def setup_database():
    conn = sqlite3.connect("osce_platform.db")
    cursor = conn.cursor()

    # 1. Scenarios Table: Stores the patient persona and grading rules
    cursor.execute('''CREATE TABLE IF NOT EXISTS scenarios 
                      (id TEXT PRIMARY KEY, name TEXT, patient_prompt TEXT, rubric TEXT)''')

    # 2. Attempts Table: Stores student results (MUST include 'transcript' to prevent UI errors)
    cursor.execute('''CREATE TABLE IF NOT EXISTS attempts 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       student_name TEXT, 
                       score INTEGER, 
                       feedback TEXT, 
                       transcript TEXT)''')

    # --- RUBRIC DATA DEFINITIONS ---

    chest_pain_rubric = [
        {"category": "Opening", "item": "Introduces themselves", "completed": False, "points": 1},
        {"category": "Opening", "item": "Confirms patient details", "completed": False, "points": 1},
        {"category": "Opening", "item": "Establishes presenting complaint using open questioning", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES (Site, Onset, Character, Radiation, Assoc. Symptoms, Time, Exacerbating/Relieving, Severity)", "completed": False, "points": 1},
        {"category": "HPC", "item": "Asks if patient has experienced this symptom previously", "completed": False, "points": 1},
        {"category": "HPC", "item": "Elicits patient’s ideas, concerns and expectations (ICE)", "completed": False, "points": 1},
        {"category": "PMH", "item": "Hypertension / Hyperlipidaemia / Diabetes", "completed": False, "points": 1},
        {"category": "PMH", "item": "Previous cardiovascular disease", "completed": False, "points": 1},
        {"category": "DH", "item": "Medications and ALLERGIES", "completed": False, "points": 1},
        {"category": "FH", "item": "Family history of CVD", "completed": False, "points": 1},
        {"category": "SH", "item": "Smoking / Alcohol / Occupation", "completed": False, "points": 1},
        {"category": "Communication", "item": "Active listening and Signposting", "completed": False, "points": 1}
    ]

    abdominal_pain_rubric = [
        {"category": "Opening", "item": "Wash hands, Don PPE, Introduce self", "completed": False, "points": 1},
        {"category": "Opening", "item": "Confirm patient details and Gain consent", "completed": False, "points": 1},
        {"category": "HPC", "item": "Location, Onset, Character, Radiation of pain", "completed": False, "points": 1},
        {"category": "HPC", "item": "Associated symptoms / Exacerbating and relieving factors", "completed": False, "points": 1},
        {"category": "HPC", "item": "Screen for GI symptoms (Nausea, Bowel habit, Weight loss, Jaundice)", "completed": False, "points": 1},
        {"category": "HPC", "item": "Screen for Urological symptoms (Dysuria, Frequency, Haematuria)", "completed": False, "points": 1},
        {"category": "HPC", "item": "Screen for Gynaecological symptoms (Vaginal discharge/bleeding, Pregnancy)", "completed": False, "points": 1},
        {"category": "HPC", "item": "Ideas, Concerns, Expectations (ICE)", "completed": False, "points": 1},
        {"category": "PMH", "item": "Medical conditions and Surgical history", "completed": False, "points": 1},
        {"category": "DH", "item": "Medications and Allergies", "completed": False, "points": 1},
        {"category": "FH", "item": "Family history of GI disease", "completed": False, "points": 1},
        {"category": "SH", "item": "Diet, Weight, Smoking, Alcohol", "completed": False, "points": 1},
        {"category": "Closing", "item": "Summarise, Thank patient, Wash hands", "completed": False, "points": 1}
    ]

    back_pain_rubric = [
        {"category": "Opening", "item": "Introduces self and Confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES pain assessment", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Cauda Equina (Saddle anaesthesia, Bladder/Bowel dysfunction)", "completed": False, "points": 5},
        {"category": "Red Flags", "item": "Spinal Fracture (Trauma, Sudden onset)", "completed": False, "points": 5},
        {"category": "Red Flags", "item": "Malignancy (Weight loss, History of cancer, Age >50)", "completed": False, "points": 5},
        {"category": "Red Flags", "item": "Infection (Fever, IV drug use, Immunosuppression)", "completed": False, "points": 5},
        {"category": "PMH", "item": "Previous back pain, Osteoporosis, or Scoliosis", "completed": False, "points": 1},
        {"category": "DH", "item": "Analgesia, Steroid use, and Allergies", "completed": False, "points": 1},
        {"category": "SH", "item": "Occupation, Stress levels, and Exercise", "completed": False, "points": 1},
        {"category": "Closing", "item": "Summarises and Thanks patient", "completed": False, "points": 1}
    ]

    # 3. Insert Stations
    scenarios = [
        (
            'chest_pain', 
            'Chest Pain Station', 
            'You are Mr. Jones, 65, with crushing chest pain. You are sweaty and pale. Do not describe your gestures or your physical actions. Do not offer up any medical history or detail about your symptoms unless prompted.', 
            json.dumps(chest_pain_rubric)
        ),
        (
            'abdominal_pain', 
            'Abdominal Pain Station', 
            'You are Mrs. Smith, 40, with sharp right-upper-quadrant pain after a fatty meal. Do not describe your gestures or your physical actions. Do not offer up any medical history or detail about your symptoms unless prompted.', 
            json.dumps(abdominal_pain_rubric)
        ),
        (
            'back_pain', 
            'Back Pain Station', 
            'You are Mr. Taylor, 30, with lower back pain and numbness in your legs. Do not describe your gestures or your physical actions. Do not offer up any medical history or detail about your symptoms unless prompted.', 
            json.dumps(back_pain_rubric)
        )
    ]

    cursor.executemany("INSERT OR REPLACE INTO scenarios VALUES (?, ?, ?, ?)", scenarios)
    
    conn.commit()
    conn.close()
    print("Database setup complete. All stations and transcript column added.")

if __name__ == "__main__":
    setup_database()
