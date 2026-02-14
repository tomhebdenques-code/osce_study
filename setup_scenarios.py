import sqlite3
import json
import os

def setup_database():
    db_name = "osce_platform.db"
    
    # Remove old DB if exists to ensure clean slate for new schema
    if os.path.exists(db_name):
        os.remove(db_name)
        print("⚠️ Old database removed. Creating fresh instance...")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create Scenarios Table
    cursor.execute('''CREATE TABLE scenarios 
                      (id TEXT PRIMARY KEY, 
                       name TEXT, 
                       patient_prompt TEXT, 
                       rubric TEXT, 
                       viva_questions TEXT)''')

    # Create Attempts Table
    cursor.execute('''CREATE TABLE attempts 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       student_name TEXT, 
                       score INTEGER, 
                       feedback TEXT, 
                       transcript TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # --- EXISTING STATIONS ---

    chest_pain_rubric = [
        {"category": "Opening", "item": "Introduces themselves", "completed": False, "points": 1},
        {"category": "Opening", "item": "Confirms patient details", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES assessment", "completed": False, "points": 1},
        {"category": "HPC", "item": "Asks about previous episodes", "completed": False, "points": 1},
        {"category": "Risk Factors", "item": "Smoking/Alcohol history", "completed": False, "points": 1},
        {"category": "Risk Factors", "item": "Family History of CVD", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Asks about palpitations/dizziness", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Asks about shortness of breath", "completed": False, "points": 1},
        {"category": "ICE", "item": "Elicits Ideas, Concerns, Expectations", "completed": False, "points": 1},
        {"category": "Closing", "item": "Summarises and Safety Nets", "completed": False, "points": 1}
    ]

    chest_pain_viva = [
        {"q": "What are your top three differentials?", "model": "ACS (MI/Angina), Pulmonary Embolism, Aortic Dissection"},
        {"q": "Immediate management for suspected ACS?", "model": "MONA: Morphine, Oxygen (if sat <94%), Nitrates (GTN), Aspirin 300mg"},
        {"q": "What is the timeframe for a primary PCI?", "model": "Within 120 minutes of first medical contact"}
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
        {"category": "Closing", "item": "Summarises findings", "completed": False, "points": 1}
    ]

    abdominal_pain_viva = [
        {"q": "What is the most likely diagnosis?", "model": "Acute Cholecystitis or Biliary Colic"},
        {"q": "Which physical sign confirms suspicion of cholecystitis?", "model": "Murphy's Sign (inspiratory arrest on RUQ palpation)"},
        {"q": "Gold-standard initial imaging?", "model": "Abdominal Ultrasound (RUQ)"}
    ]

    back_pain_rubric = [
        {"category": "Opening", "item": "Introduces and confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "SOCRATES assessment", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Saddle Anaesthesia", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bladder dysfunction (retention/incontinence)", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bowel dysfunction (incontinence)", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Bilateral Leg weakness", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "History of Cancer or Trauma", "completed": False, "points": 1},
        {"category": "ICE", "item": "Elicits ICE", "completed": False, "points": 1}
    ]

    back_pain_viva = [
        {"q": "Most serious neuro emergency to rule out?", "model": "Cauda Equina Syndrome"},
        {"q": "Gold-standard investigation and timeframe?", "model": "MRI Whole Spine within 4-6 hours"},
        {"q": "Definitive management if confirmed?", "model": "Emergency surgical decompression"}
    ]

    # --- NEW STATIONS (COMPETITOR INSPIRED) ---

    neuro_headache_rubric = [
        {"category": "Opening", "item": "Introduces and confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "Onset speed (Thunderclap vs Gradual)", "completed": False, "points": 2},
        {"category": "HPC", "item": "Severity (1-10)", "completed": False, "points": 1},
        {"category": "Associated Sx", "item": "Photophobia / Neck Stiffness", "completed": False, "points": 1},
        {"category": "Associated Sx", "item": "Vomiting or Visual disturbance", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "History of trauma", "completed": False, "points": 1},
        {"category": "PMH", "item": "Previous headaches (Migraine history)", "completed": False, "points": 1},
        {"category": "DH", "item": "Anticoagulants use", "completed": False, "points": 1},
        {"category": "FH", "item": "Family history of Brain Aneurysm", "completed": False, "points": 1},
        {"category": "Closing", "item": "Explanation of need for CT Head", "completed": False, "points": 1}
    ]

    neuro_headache_viva = [
        {"q": "What is the critical 'cannot miss' diagnosis here?", "model": "Subarachnoid Hemorrhage (SAH)"},
        {"q": "If CT Head is negative but suspicion remains, what next?", "model": "Lumbar Puncture (checking for xanthochromia) after 12 hours"},
        {"q": "What is the characteristic description of an SAH?", "model": "Thunderclap headache, 'kicked in the back of the head'"}
    ]

    resp_asthma_rubric = [
        {"category": "Opening", "item": "Introduces and confirms details", "completed": False, "points": 1},
        {"category": "HPC", "item": "Triggers (Dust, Pets, Cold Air)", "completed": False, "points": 1},
        {"category": "HPC", "item": "Diurnal variation (worse at night)", "completed": False, "points": 1},
        {"category": "Severity", "item": "Ability to complete sentences", "completed": False, "points": 1},
        {"category": "History", "item": "Previous ICU admissions / Intubation", "completed": False, "points": 2},
        {"category": "DH", "item": "Inhaler technique and compliance", "completed": False, "points": 1},
        {"category": "DH", "item": "Steroid use (Oral)", "completed": False, "points": 1},
        {"category": "SH", "item": "Smoking status", "completed": False, "points": 1},
        {"category": "Atopic", "item": "History of Eczema or Hayfever", "completed": False, "points": 1}
    ]

    resp_asthma_viva = [
        {"q": "What defines 'Life Threatening' Asthma?", "model": "Silent chest, Cyanosis, Poor respiratory effort, Bradycardia, PEF < 33%"},
        {"q": "Describe the immediate medical management steps (O SHIT).", "model": "Oxygen, Salbutamol (nebs), Hydrocortisone (IV) / Prednisolone, Ipratropium (nebs), Theophylline/Magnesium (IV)"},
        {"q": "What is the typical blood gas finding in early asthma attack?", "model": "Respiratory Alkalosis (due to hyperventilation). Normal or high CO2 is a danger sign."}
    ]

    paeds_fever_rubric = [
        {"category": "Opening", "item": "Introduces to Parent", "completed": False, "points": 1},
        {"category": "HPC", "item": "Duration and height of fever", "completed": False, "points": 1},
        {"category": "Hydration", "item": "Wet nappies / fluid intake", "completed": False, "points": 2},
        {"category": "Behavior", "item": "Irritability / Drowsiness", "completed": False, "points": 1},
        {"category": "Red Flags", "item": "Rash (Non-blanching)", "completed": False, "points": 2},
        {"category": "Red Flags", "item": "Fits or Seizures", "completed": False, "points": 1},
        {"category": "Birth Hx", "item": "Gestation / Delivery complications", "completed": False, "points": 1},
        {"category": "Imms", "item": "Vaccination status up to date", "completed": False, "points": 1},
        {"category": "Safety Net", "item": "Advice on when to return", "completed": False, "points": 1}
    ]

    paeds_fever_viva = [
        {"q": "What are the traffic light system categories for fever?", "model": "Green (Low risk), Amber (Intermediate), Red (High risk)"},
        {"q": "Name two 'Red' features in a febrile child.", "model": "Non-blanching rash, bulging fontanelle, neck stiffness, status epilepticus, focal neuro signs"},
        {"q": "Empiric antibiotic for suspected meningitis in <3 months old?", "model": "IV Cefotaxime (plus Amoxicillin for Listeria coverage)"}
    ]

    scenarios = [
        ('chest_pain', 'Chest Pain', 'You are Mr. Jones, 65. You have crushing central chest pain that started 1 hour ago while gardening. It radiates to your left arm. You feel sweaty and nauseous. You smoke 20 a day. You are worried about a heart attack.', json.dumps(chest_pain_rubric), json.dumps(chest_pain_viva)),
        ('abdominal_pain', 'Abdominal Pain', 'You are Mrs. Smith, 40. You have sharp pain in the top right of your tummy (RUQ). It started after a takeaway last night. It goes to your right shoulder. You feel hot and sick. No jaundice.', json.dumps(abdominal_pain_rubric), json.dumps(abdominal_pain_viva)),
        ('back_pain', 'Back Pain', 'You are Mr. Taylor, 30. You have lower back pain after lifting a box at work. Pain is 6/10. Crucially: You have had some numbness between your legs (saddle area) and you wet yourself earlier (incontinence).', json.dumps(back_pain_rubric), json.dumps(back_pain_viva)),
        ('headache', 'Thunderclap Headache', 'You are Sarah, 45. You were at the gym and suddenly felt like someone hit you in the back of the head with a bat. It is the worst pain ever (10/10). You vomited once. Light hurts your eyes.', json.dumps(neuro_headache_rubric), json.dumps(neuro_headache_viva)),
        ('asthma', 'Asthma Attack', 'You are Ben, 22. You are struggling to breathe. You have asthma but lost your brown inhaler. You have used your blue one 10 times today but it is not working. You speak in short sentences. Wheezy.', json.dumps(resp_asthma_rubric), json.dumps(resp_asthma_viva)),
        ('paeds_fever', 'Febrile Child (Parent)', 'You are the mother of Leo, 18 months old. He has been hot for 2 days. He is very sleepy and hard to wake up. He has not had a wet nappy for 12 hours. You are terrified.', json.dumps(paeds_fever_rubric), json.dumps(paeds_fever_viva))
    ]

    cursor.executemany("INSERT INTO scenarios VALUES (?,?,?,?,?)", scenarios)
    conn.commit()
    conn.close()
    print("✅ Database Synchronized: 6 Stations Loaded.")

if __name__ == "__main__":
    setup_database()