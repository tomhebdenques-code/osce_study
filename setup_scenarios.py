import sqlite3
import json
import os

def setup_database():
    db_name = "osce_platform.db"
    
    # Remove old DB to ensure clean slate
    if os.path.exists(db_name):
        os.remove(db_name)
        print("⚠️ Old database removed. Creating fresh instance with 50 Stations...")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create Tables
    cursor.execute('''CREATE TABLE scenarios 
                      (id TEXT PRIMARY KEY, 
                       name TEXT, 
                       patient_prompt TEXT, 
                       rubric TEXT, 
                       viva_questions TEXT)''')

    cursor.execute('''CREATE TABLE attempts 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       student_name TEXT, 
                       score INTEGER, 
                       feedback TEXT, 
                       transcript TEXT,
                       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # --- HELPER: STANDARD RUBRIC TEMPLATES ---
    # These base templates are customized per station to ensure high-quality consistent marking
    
    def get_standard_rubric(specific_items):
        base = [
            {"category": "Opening", "item": "Introduces self & role", "completed": False, "points": 1},
            {"category": "Opening", "item": "Confirms patient ID", "completed": False, "points": 1},
            {"category": "HPC", "item": "Open questioning style", "completed": False, "points": 1},
            {"category": "ICE", "item": "Ideas, Concerns, Expectations", "completed": False, "points": 2},
            {"category": "Closing", "item": "Summary & Safety Net", "completed": False, "points": 1}
        ]
        return base + specific_items

    # --- STATION DATA (50 SCENARIOS) ---
    
    stations_data = [
        # --- CARDIOLOGY ---
        {
            "id": "cardio_chest_pain",
            "name": "Chest Pain (MI)",
            "prompt": "You are Mr. Jones, 65. Crushing central chest pain for 1 hour. Radiates to left arm. Sweaty, nauseous. Smoker (20/day). Worried it's a heart attack.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "SOCRATES Assessment", "completed": False, "points": 1},
                {"category": "Risk", "item": "Smoking/Family History", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Autonomic symptoms (sweat/nausea)", "completed": False, "points": 1},
                {"category": "DDx", "item": "Rule out dissection/PE questions", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Management?", "model": "MONA (Morphine, Oxygen, Nitrates, Aspirin) + PCI"}, {"q": "ECG signs?", "model": "ST Elevation"}]
        },
        {
            "id": "cardio_afib",
            "name": "Palpitations (AF)",
            "prompt": "You are Mrs. Green, 72. You feel your heart 'fluttering' or 'racing' irregularly. Mild breathlessness. No pain. History of hypertension.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Onset/Termination of palpitations", "completed": False, "points": 1},
                {"category": "Assoc", "item": "Syncope/Dizziness check", "completed": False, "points": 1},
                {"category": "Triggers", "item": "Caffeine/Alcohol/Stress", "completed": False, "points": 1},
                {"category": "PMH", "item": "Thyroid/Heart issues", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "ECG findings?", "model": "Absent P waves, irregularly irregular QRS"}, {"q": "Stroke risk score?", "model": "CHADS2-VASC"}]
        },
        {
            "id": "cardio_syncope",
            "name": "Syncope (Aortic Stenosis)",
            "prompt": "You are Mr. Ali, 75. You fainted while walking up a hill. You have been feeling short of breath on exertion recently. No chest pain today.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Events before/during/after", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Injury during fall", "completed": False, "points": 1},
                {"category": "Review", "item": "Exercise tolerance check", "completed": False, "points": 1},
                {"category": "Family", "item": "Sudden cardiac death history", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Classic triad of AS?", "model": "Syncope, Angina, Dyspnea"}, {"q": "Murmur type?", "model": "Ejection Systolic, radiates to carotids"}]
        },
        {
            "id": "cardio_hf",
            "name": "Heart Failure",
            "prompt": "You are Mrs. White, 80. Increasing ankle swelling and shortness of breath when lying flat (orthopnea). You sleep with 3 pillows.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Orthopnea / PND check", "completed": False, "points": 1},
                {"category": "HPC", "item": "Exercise tolerance", "completed": False, "points": 1},
                {"category": "PMH", "item": "Ischaemic heart disease history", "completed": False, "points": 1},
                {"category": "Social", "item": "Impact on daily living", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Blood test for HF?", "model": "BNP (B-type Natriuretic Peptide)"}, {"q": "1st line drugs?", "model": "ACE inhibitor + Beta Blocker"}]
        },
        {
            "id": "cardio_htn",
            "name": "Hypertension Review",
            "prompt": "You are Mr. Clark, 50. Here for a BP check. It was 150/95 last time. You feel fine. You drink 30 units of alcohol a week.",
            "rubric": get_standard_rubric([
                {"category": "Asymptomatic", "item": "Checks for vision/headache issues", "completed": False, "points": 1},
                {"category": "Lifestyle", "item": "Alcohol/Salt/Exercise history", "completed": False, "points": 1},
                {"category": "Family", "item": "Premature CVD history", "completed": False, "points": 1},
                {"category": "Plan", "item": "Discusses lifestyle changes", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Clinic BP cutoff?", "model": "140/90"}, {"q": "End organ damage to check?", "model": "Retinopathy, Nephropathy, LVH"}]
        },

        # --- RESPIRATORY ---
        {
            "id": "resp_asthma",
            "name": "Acute Asthma",
            "prompt": "You are Ben, 22. Struggling to breathe. Wheezy. Lost inhaler. Used blue inhaler 10 times, not working. Speak in short phrases.",
            "rubric": get_standard_rubric([
                {"category": "Severity", "item": "Ability to speak sentences", "completed": False, "points": 1},
                {"category": "History", "item": "Previous ICU/Intubation", "completed": False, "points": 2},
                {"category": "Triggers", "item": "Allergies/Cold/Stress", "completed": False, "points": 1},
                {"category": "Current", "item": "Inhaler usage today", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Life threatening signs?", "model": "Silent chest, Cyanosis, PEF <33%"}, {"q": "Management?", "model": "O SHIT (Oxygen, Salbutamol, Hydrocortisone, Ipratropium, Theophylline)"}]
        },
        {
            "id": "resp_copd",
            "name": "COPD Exacerbation",
            "prompt": "You are Mr. Smith, 70. Smoked 50 years. Coughing up green phlegm for 3 days. More breathless than usual. Feverish.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Sputum colour/quantity", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Fever/Confusion check", "completed": False, "points": 1},
                {"category": "Baseline", "item": "Normal exercise tolerance", "completed": False, "points": 1},
                {"category": "Meds", "item": "Home oxygen/Nebulizers", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "O2 Target?", "model": "88-92% (Risk of CO2 retention)"}, {"q": "Organism causes?", "model": "H. Influenzae, Strep. Pneumoniae, Moraxella"}]
        },
        {
            "id": "resp_pe",
            "name": "Pulmonary Embolism",
            "prompt": "You are Sarah, 35. Sudden onset sharp right sided chest pain and breathlessness. Just returned from a long haul flight from Australia.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Pleuritic nature of pain", "completed": False, "points": 1},
                {"category": "Risk", "item": "Long haul travel/Immobility", "completed": False, "points": 1},
                {"category": "Risk", "item": "OCP/Hormone use", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Haemoptysis/Syncope", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Scoring system?", "model": "Wells Score"}, {"q": "Gold standard investigation?", "model": "CT Pulmonary Angiogram (CTPA)"}]
        },
        {
            "id": "resp_pneumonia",
            "name": "Pneumonia",
            "prompt": "You are Mr. Brown, 55. High fever, shaking chills (rigors), productive cough with rusty sputum. Pain when breathing in on right side.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Sputum description", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Fever/Rigors", "completed": False, "points": 1},
                {"category": "Social", "item": "Alcohol use (aspiration risk)", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Confusion (AMTS)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Severity score?", "model": "CURB-65"}, {"q": "Commonest organism?", "model": "Streptococcus Pneumoniae"}]
        },
        {
            "id": "resp_ca",
            "name": "Haemoptysis (Lung Ca)",
            "prompt": "You are Mr. T, 68. Coughed up blood twice this week. Lost weight recently (5kg). Chronic smoker. Tired.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Quantity of blood/frequency", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Weight loss/Night sweats", "completed": False, "points": 1},
                {"category": "Local", "item": "Hoarseness (RLN palsy)", "completed": False, "points": 1},
                {"category": "Social", "item": "Pack year history", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Urgent referral timeframe?", "model": "2 Week Wait (2WW)"}, {"q": "Paraneoplastic signs?", "model": "Hypercalcemia, SIADH, Cushing's"}]
        },

        # --- GASTROENTEROLOGY ---
        {
            "id": "gi_chole",
            "name": "Abdominal Pain (RUQ)",
            "prompt": "You are Mrs. Smith, 40. Sharp RUQ pain after fatty food. Radiates to shoulder. Hot and nauseous. No jaundice.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Radiation to shoulder", "completed": False, "points": 1},
                {"category": "Triggers", "item": "Fatty meals", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Fever/Rigors", "completed": False, "points": 1},
                {"category": "Exam", "item": "Mentions Murphy's Sign", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Diagnosis?", "model": "Acute Cholecystitis"}, {"q": "Imaging?", "model": "Abdominal Ultrasound"}]
        },
        {
            "id": "gi_ibd",
            "name": "Diarrhoea (IBD)",
            "prompt": "You are Leo, 24. Bloody diarrhoea 6 times a day for 3 weeks. Abdominal cramps. Feeling tired and losing weight.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Stool frequency/Blood/Mucus", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Weight loss/Fever", "completed": False, "points": 1},
                {"category": "Extra-intestinal", "item": "Eye/Joint/Skin issues", "completed": False, "points": 1},
                {"category": "Family", "item": "History of IBD", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Stool test?", "model": "Faecal Calprotectin"}, {"q": "UC vs Crohn's pathology?", "model": "UC: Continuous/Superficial. Crohn's: Skip lesions/Transmural"}]
        },
        {
            "id": "gi_gord",
            "name": "Dyspepsia (GORD)",
            "prompt": "You are Mr. P, 45. Burning chest pain after meals and when lying down. Acid taste in mouth. OTC antacids help.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Relation to food/lying flat", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Dysphagia/Weight loss", "completed": False, "points": 1},
                {"category": "Lifestyle", "item": "Alcohol/Caffeine/Weight", "completed": False, "points": 1},
                {"category": "Meds", "item": "NSAID use", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Red flag for endoscopy?", "model": "Dysphagia, Weight loss, Age >55 new symptoms"}, {"q": "Organism to test?", "model": "H. Pylori"}]
        },
        {
            "id": "gi_appendicitis",
            "name": "Appendicitis",
            "prompt": "You are Jake, 18. Pain started around belly button, now moved to lower right side. Vomited once. Pain on movement.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Migration of pain", "completed": False, "points": 1},
                {"category": "Assoc", "item": "Anorexia/Nausea", "completed": False, "points": 1},
                {"category": "Urinary", "item": "Rule out UTI symptoms", "completed": False, "points": 1},
                {"category": "Exam", "item": "Mentions McBurney's point", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Sign of perforation?", "model": "Peritonitis (Rigidity/Guarding)"}, {"q": "Management?", "model": "Laparoscopic Appendicectomy"}]
        },
        {
            "id": "gi_bleed",
            "name": "Upper GI Bleed",
            "prompt": "You are Mr. V, 50. Vomited bright red blood this morning. History of heavy alcohol use and liver problems.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Quantity/Coffee ground vs Red", "completed": False, "points": 1},
                {"category": "PMH", "item": "Liver disease/Varices", "completed": False, "points": 1},
                {"category": "Meds", "item": "Anticoagulants/NSAIDs", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Signs of shock (dizziness)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Score for intervention?", "model": "Blatchford Score"}, {"q": "Management of varices?", "model": "Terlipressin + Antibiotics + Endoscopic Banding"}]
        },

        # --- NEUROLOGY ---
        {
            "id": "neuro_sah",
            "name": "Thunderclap Headache",
            "prompt": "You are Sarah, 45. Sudden 'hit on head' pain at gym. 10/10 severity. Vomited. Photophobia. Neck stiff.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Thunderclap (max <5 mins)", "completed": False, "points": 2},
                {"category": "Assoc", "item": "Meningism (Neck stiffness/Light)", "completed": False, "points": 1},
                {"category": "Family", "item": "PCKD or Aneurysm history", "completed": False, "points": 1},
                {"category": "Plan", "item": "CT Head ASAP", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Diagnosis?", "model": "Subarachnoid Haemorrhage"}, {"q": "Investigation if CT negative?", "model": "Lumbar Puncture (12hrs later for Xanthochromia)"}]
        },
        {
            "id": "neuro_stroke",
            "name": "Stroke/TIA",
            "prompt": "You are Mrs. D, 70. Right arm and face went weak for 30 mins yesterday. Back to normal now. Worried.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "FAST symptoms check", "completed": False, "points": 1},
                {"category": "Timing", "item": "Duration (<24hrs = TIA)", "completed": False, "points": 1},
                {"category": "Risk", "item": "AF/Hypertension/Smoking", "completed": False, "points": 1},
                {"category": "Exclude", "item": "Hypoglycaemia/Seizure mimics", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "TIA Management?", "model": "Aspirin 300mg stat + MRI + Specialist review (ABCD2 score outdated but relevant)"}, {"q": "Thrombolysis window?", "model": "4.5 hours"}]
        },
        {
            "id": "neuro_migraine",
            "name": "Migraine",
            "prompt": "You are Jane, 25. Recurring unilateral throbbing headaches. Visual zigzag lines before they start. Nauseous. Need to lie in dark.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Aura description", "completed": False, "points": 1},
                {"category": "Triggers", "item": "Chocolate/Cheese/Stress/Period", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Waking from sleep/Focal signs", "completed": False, "points": 1},
                {"category": "Impact", "item": "Days off work", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Acute treatment?", "model": "Triptans + NSAIDs"}, {"q": "Prophylaxis?", "model": "Propranolol or Topiramate"}]
        },
        {
            "id": "neuro_parkinsons",
            "name": "Parkinson's History",
            "prompt": "You are Mr. H, 70. Hands shake when resting. Feel slow to get going. Wife says I walk with small steps and don't smile anymore.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Tremor (Resting/Pill rolling)", "completed": False, "points": 1},
                {"category": "HPC", "item": "Bradykinesia/Rigidity symptoms", "completed": False, "points": 1},
                {"category": "Non-motor", "item": "Sleep/Smell/Mood changes", "completed": False, "points": 1},
                {"category": "Func", "item": "Buttons/Writing (Micrographia)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Core triad?", "model": "Bradykinesia, Resting Tremor, Rigidity"}, {"q": "Main drug?", "model": "Levodopa (with Carbidopa)"}]
        },
        {
            "id": "neuro_seizure",
            "name": "First Seizure",
            "prompt": "You are Alex, 20. Woke up in ambulance. Friends say you fell and shook on the floor for 2 mins. Bit your tongue. Wet yourself.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Pre-ictal (Aura/Deja vu)", "completed": False, "points": 1},
                {"category": "Ictal", "item": "Tongue bite/Incontinence", "completed": False, "points": 1},
                {"category": "Post-ictal", "item": "Confusion/Drowsiness", "completed": False, "points": 1},
                {"category": "Safety", "item": "Driving/Swimming/Heights advice", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Driving rule (UK)?", "model": "Stop driving, inform DVLA, usually 1 year off"}, {"q": "Red flag cause?", "model": "Tumour / Bleed / Infection"}]
        },

        # --- MSK ---
        {
            "id": "msk_back",
            "name": "Back Pain (Cauda Equina)",
            "prompt": "You are Mr. Taylor, 30. Back pain after lifting. Numbness between legs (saddle). Urinary incontinence. 6/10 pain.",
            "rubric": get_standard_rubric([
                {"category": "Red Flags", "item": "Saddle Anaesthesia", "completed": False, "points": 2},
                {"category": "Red Flags", "item": "Bladder/Bowel dysfunction", "completed": False, "points": 2},
                {"category": "Red Flags", "item": "Bilateral weakness", "completed": False, "points": 1},
                {"category": "HPC", "item": "Mechanism of injury", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Diagnosis?", "model": "Cauda Equina Syndrome"}, {"q": "Management?", "model": "Urgent MRI Spine + Surgical Decompression"}]
        },
        {
            "id": "msk_gout",
            "name": "Gout",
            "prompt": "You are Mr. G, 55. Woke up with excruciating pain in right big toe. Red, hot, swollen. Can't put sheets on it. Drink beer.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "First MTP joint involvement", "completed": False, "points": 1},
                {"category": "Risk", "item": "Alcohol/Diet/Diuretics", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Fever (Rule out septic arthritis)", "completed": False, "points": 1},
                {"category": "PMH", "item": "Previous episodes", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Aspirate finding?", "model": "Negatively birefringent needle-shaped crystals"}, {"q": "Acute Treatment?", "model": "NSAIDs / Colchicine"}]
        },
        {
            "id": "msk_ra",
            "name": "Rheumatoid Arthritis",
            "prompt": "You are Mrs. R, 45. Pain and stiffness in both hands. Worse in mornings (>1 hour). Fatigue.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Symmetrical small joints", "completed": False, "points": 1},
                {"category": "Stiffness", "item": "Morning stiffness duration", "completed": False, "points": 1},
                {"category": "Systemic", "item": "Fatigue/Malaise", "completed": False, "points": 1},
                {"category": "Impact", "item": "ADLs (dressing/cooking)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Antibodies?", "model": "Rheumatoid Factor + Anti-CCP (Specific)"}, {"q": "Mainstay treatment?", "model": "DMARDs (Methotrexate)"}]
        },
        {
            "id": "msk_knee",
            "name": "Knee Injury (ACL)",
            "prompt": "You are Tom, 25. Twisted knee playing football. Heard a 'pop'. Immediate swelling. Knee feels unstable/gives way.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Mechanism (twisting)", "completed": False, "points": 1},
                {"category": "HPC", "item": "Audible 'pop' / Rapid swelling", "completed": False, "points": 1},
                {"category": "Mech", "item": "Locking vs Giving way", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Ability to weight bear (Ottowa rules)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Special test?", "model": "Anterior Drawer / Lachman's"}, {"q": "Imaging?", "model": "MRI"}]
        },
        {
            "id": "msk_shoulder",
            "name": "Frozen Shoulder",
            "prompt": "You are Mrs. F, 50. Stiff and painful right shoulder. Hard to brush hair or fasten bra. Diabetic.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "External rotation limitation", "completed": False, "points": 1},
                {"category": "PMH", "item": "Diabetes link", "completed": False, "points": 1},
                {"category": "Differentiate", "item": "Active vs Passive movement", "completed": False, "points": 1},
                {"category": "Impact", "item": "Function/Sleep", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Medical name?", "model": "Adhesive Capsulitis"}, {"q": "Phases?", "model": "Freezing, Frozen, Thawing"}]
        },

        # --- PSYCHIATRY ---
        {
            "id": "psych_dep",
            "name": "Depression",
            "prompt": "You are John, 30. Low mood for 3 months. No enjoyment (anhedonia). Early morning waking. Weight loss. 'Better off dead'.",
            "rubric": get_standard_rubric([
                {"category": "Core", "item": "Low mood + Anhedonia + Fatigue", "completed": False, "points": 2},
                {"category": "Biological", "item": "Sleep/Appetite/Libido", "completed": False, "points": 1},
                {"category": "Cognitive", "item": "Concentration/Guilt/Worthlessness", "completed": False, "points": 1},
                {"category": "Risk", "item": "Suicide intent/planning", "completed": False, "points": 2}
            ]),
            "viva": [{"q": "ICD-10 criteria duration?", "model": "> 2 weeks"}, {"q": "1st line med?", "model": "SSRI (Sertraline/Citalopram)"}]
        },
        {
            "id": "psych_anx",
            "name": "Generalised Anxiety",
            "prompt": "You are Sarah, 24. Worry about everything all the time. On edge. Poor sleep. Palpitations. Affecting work.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Constant free-floating worry", "completed": False, "points": 1},
                {"category": "Physical", "item": "Palpitations/Sweating/Tension", "completed": False, "points": 1},
                {"category": "Exclude", "item": "Panic attacks/Thyroid symptoms", "completed": False, "points": 1},
                {"category": "Coping", "item": "Alcohol/Drugs use", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Differential?", "model": "Hyperthyroidism"}, {"q": "Therapy?", "model": "CBT"}]
        },
        {
            "id": "psych_alch",
            "name": "Alcohol Dependence",
            "prompt": "You are Mr. Walker, 45. Drink 1 bottle vodka/day. Hands shake in morning. Need a drink to stop shaking (eye-opener).",
            "rubric": get_standard_rubric([
                {"category": "Quantify", "item": "Units calculation", "completed": False, "points": 1},
                {"category": "Dependence", "item": "CAGE questions / Withdrawal signs", "completed": False, "points": 2},
                {"category": "Complications", "item": "Liver/Falls/Memory", "completed": False, "points": 1},
                {"category": "Social", "item": "Job/Family impact", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Withdrawal scale?", "model": "CIWA-Ar"}, {"q": "Vitamin prophylaxis?", "model": "Thiamine (Pabrinex) for Wernicke's"}]
        },
        {
            "id": "psych_psycho",
            "name": "First Episode Psychosis",
            "prompt": "You are Leo, 19. You hear voices commenting on your actions. You think the TV is sending you messages. You stopped going to uni.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Auditory Hallucinations (3rd person)", "completed": False, "points": 1},
                {"category": "HPC", "item": "Delusions (Reference/Persecution)", "completed": False, "points": 1},
                {"category": "HPC", "item": "Passivity phenomena", "completed": False, "points": 1},
                {"category": "Risk", "item": "Command hallucinations", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Key Differential?", "model": "Drug induced psychosis"}, {"q": "Management?", "model": "Early Intervention Team + Antipsychotics"}]
        },
        {
            "id": "psych_mania",
            "name": "Mania (Bipolar)",
            "prompt": "You are Dan, 28. Feel amazing. Haven't slept for 3 days. Spending all money. Talk very fast. 'I am the next messiah'.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Elevated mood/Irritability", "completed": False, "points": 1},
                {"category": "HPC", "item": "Pressured speech/Flight of ideas", "completed": False, "points": 1},
                {"category": "HPC", "item": "Grandiosity/Spending/Risky sex", "completed": False, "points": 1},
                {"category": "Safety", "item": "Risk to reputation/finances", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Medication?", "model": "Lithium / Antipsychotic / Valproate"}, {"q": "Lithium toxicity sign?", "model": "Coarse tremor, vomiting, ataxia"}]
        },

        # --- PAEDIATRICS ---
        {
            "id": "paeds_fever",
            "name": "Febrile Child",
            "prompt": "You are Mother of Leo, 18mo. Hot for 2 days. Very sleepy. No wet nappy 12hrs. Non-blanching rash on leg.",
            "rubric": get_standard_rubric([
                {"category": "Red Flags", "item": "Non-blanching rash", "completed": False, "points": 2},
                {"category": "Red Flags", "item": "Dehydration signs (nappies)", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Drowsiness", "completed": False, "points": 1},
                {"category": "Birth", "item": "Vaccination status", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Traffic light system?", "model": "Green/Amber/Red (NICE)"}, {"q": "Meningitis treatment?", "model": "IM/IV Ceftriaxone/Cefotaxime"}]
        },
        {
            "id": "paeds_croup",
            "name": "Croup",
            "prompt": "Parent of 3yo. Barking cough like a seal. Stridor when crying. Worse at night. Mild fever.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Barking cough description", "completed": False, "points": 1},
                {"category": "Severity", "item": "Stridor at rest vs crying", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Drooling (Epiglottitis)", "completed": False, "points": 1},
                {"category": "Plan", "item": "Dexamethasone explanation", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Score used?", "model": "Wesley Croup Score"}, {"q": "Cause?", "model": "Parainfluenza virus"}]
        },
        {
            "id": "paeds_gastro",
            "name": "Gastroenteritis",
            "prompt": "Parent of 4yo. Vomiting and diarrhoea for 2 days. Not keeping fluids down. Lethargic.",
            "rubric": get_standard_rubric([
                {"category": "History", "item": "Frequency of D&V", "completed": False, "points": 1},
                {"category": "Hydration", "item": "Tears/Mucosa/Urine output", "completed": False, "points": 2},
                {"category": "Contact", "item": "Sick contacts/Nursery", "completed": False, "points": 1},
                {"category": "Plan", "item": "Fluid challenge/ORS", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Maintenance fluid calc?", "model": "100/50/20 rule (Holliday-Segar)"}, {"q": "Red flag?", "model": "Bilious vomiting (Obstruction)"}]
        },
        {
            "id": "paeds_asthma",
            "name": "Paeds Asthma",
            "prompt": "Parent of 6yo. Coughs at night and after sport. Wheezy. Eczema history. Dad smokes outside.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Interval symptoms (night/exercise)", "completed": False, "points": 1},
                {"category": "Atopy", "item": "Eczema/Hayfever history", "completed": False, "points": 1},
                {"category": "Social", "item": "Passive smoking check", "completed": False, "points": 1},
                {"category": "Inhaler", "item": "Spacer technique check", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Diagnosis?", "model": "Clinical (+/- Spirometry if older)"}, {"q": "Stepwise management?", "model": "SABA -> SABA + ICS"}]
        },
        {
            "id": "paeds_naf",
            "name": "Non-Accidental Injury",
            "prompt": "Parent of 2yo. 'Fell off sofa'. Bruise on cheek and arm. Delayed presentation (happened yesterday). You seem defensive.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Mechanism matches injury?", "completed": False, "points": 2},
                {"category": "History", "item": "Developmental stage (mobile?)", "completed": False, "points": 1},
                {"category": "Social", "item": "Who is at home/Social services", "completed": False, "points": 1},
                {"category": "Action", "item": "Full skeletal survey/Admit", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Suspicious bruises?", "model": "Triangle of safety (Ears, Neck, Cheeks), Buttocks"}, {"q": "First step?", "model": "Discuss with senior/Safeguarding lead"}]
        },

        # --- OBS & GYNAE ---
        {
            "id": "og_preg_bleed",
            "name": "Early Pregnancy Bleed",
            "prompt": "You are Lisa, 28. 7 weeks pregnant. Spotting blood and mild cramps. Worried about miscarriage. First pregnancy.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Amount of blood/Clots", "completed": False, "points": 1},
                {"category": "Pain", "item": "Shoulder tip pain (Ectopic)", "completed": False, "points": 1},
                {"category": "History", "item": "Confirm LMP/Gestation", "completed": False, "points": 1},
                {"category": "Rh", "item": "Check Rhesus status", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Investigation?", "model": "Transvaginal Ultrasound + Beta-HCG"}, {"q": "Ectopic triad?", "model": "Pain, Amenorrhea, Vaginal Bleeding"}]
        },
        {
            "id": "og_pcos",
            "name": "Amenorrhea (PCOS)",
            "prompt": "You are Sarah, 22. Periods are very irregular (every 3-4 months). Gaining weight. Acne. Trying to conceive.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Cycle length/Menarche", "completed": False, "points": 1},
                {"category": "Signs", "item": "Hirsutism/Acne/Weight", "completed": False, "points": 1},
                {"category": "Exclude", "item": "Pregnancy/Thyroid/Prolactin", "completed": False, "points": 1},
                {"category": "Impact", "item": "Fertility concerns", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Rotterdam Criteria?", "model": "2 of 3: Oligo-ovulation, Hyperandrogenism, Polycystic ovaries"}, {"q": "Long term risks?", "model": "Diabetes, Endometrial Cancer"}]
        },
        {
            "id": "og_contraception",
            "name": "Contraception Council",
            "prompt": "You are Amy, 19. Want to go on the pill. Smoker. History of migraines with aura. Boyfriend has chlamydia.",
            "rubric": get_standard_rubric([
                {"category": "Contraindications", "item": "Migraine with Aura (Stroke risk)", "completed": False, "points": 2},
                {"category": "History", "item": "Smoking/Clot risk", "completed": False, "points": 1},
                {"category": "Sexual", "item": "STI screen offer", "completed": False, "points": 1},
                {"category": "Options", "item": "Suggests LARC (Implant/Coil) or POP", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "UKMEC Score for COCP + Migraine Aura?", "model": "UKMEC 4 (Unacceptable risk)"}, {"q": "Emergency contraception windows?", "model": "Levonelle (72hr), ellaOne (120hr), Copper IUD (5 days)"}]
        },
        {
            "id": "og_menorrhagia",
            "name": "Heavy Periods",
            "prompt": "You are Mrs. T, 42. Periods are flooding, passing clots. Tired all the time. Finished family.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Quantify bleeding (pads/flooding)", "completed": False, "points": 1},
                {"category": "Red Flags", "item": "Intermenstrual/Post-coital bleed", "completed": False, "points": 1},
                {"category": "Impact", "item": "Anaemia symptoms", "completed": False, "points": 1},
                {"category": "Meds", "item": "Mirena Coil discussion", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "First line medical?", "model": "Mirena IUS"}, {"q": "Fibroids investigation?", "model": "Pelvic Ultrasound"}]
        },
        {
            "id": "og_preeclampsia",
            "name": "Pre-Eclampsia",
            "prompt": "You are Mrs. J, 34 weeks pregnant. Headache, blurred vision, swelling in hands/face. Epigastric pain.",
            "rubric": get_standard_rubric([
                {"category": "HPC", "item": "Visual disturbance/Headache", "completed": False, "points": 1},
                {"category": "Pain", "item": "Epigastric pain (Liver capsule)", "completed": False, "points": 1},
                {"category": "Fetal", "item": "Fetal movements check", "completed": False, "points": 1},
                {"category": "Plan", "item": "Urgent admission/BP check", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Definition?", "model": "HTN + Proteinuria >20 weeks"}, {"q": "Seizure prophylaxis?", "model": "Magnesium Sulphate"}]
        },

        # --- COMMUNICATION & ETHICS ---
        {
            "id": "comm_bbn",
            "name": "Breaking Bad News",
            "prompt": "You are Mr. Smith. The doctor is here to tell you your CT scan results. You suspect it is cancer but hope it isn't.",
            "rubric": get_standard_rubric([
                {"category": "Setup", "item": "Warning shot fired", "completed": False, "points": 1},
                {"category": "Information", "item": "Clear language (uses word 'Cancer')", "completed": False, "points": 2},
                {"category": "Empathy", "item": "Allows silence/response", "completed": False, "points": 1},
                {"category": "Plan", "item": "Follow up/Nurse specialist", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Framework?", "model": "SPIKES (Setting, Perception, Invitation, Knowledge, Empathy, Strategy)"}, {"q": "Key principle?", "model": "check understanding constantly"}]
        },
        {
            "id": "comm_error",
            "name": "Medical Error",
            "prompt": "You are Mrs. X. The doctor gave you penicillin, but you are allergic. You have a rash. You are angry.",
            "rubric": get_standard_rubric([
                {"category": "Opening", "item": "Open disclosure/Apology immediately", "completed": False, "points": 2},
                {"category": "Action", "item": "Explain what happened/Why", "completed": False, "points": 1},
                {"category": "Safety", "item": "Assess patient clinically (Anaphylaxis)", "completed": False, "points": 1},
                {"category": "Closing", "item": "Reporting (Datix)/Prevention", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Duty of Candour?", "model": "Legal duty to be open and honest when things go wrong"}, {"q": "Next step?", "model": "Datix/Incident report"}]
        },
        {
            "id": "comm_dnacpr",
            "name": "DNACPR Discussion",
            "prompt": "You are Daughter of Mr. H (85, advanced dementia, frail). Doctor wants to discuss CPR. You think 'you should do everything'.",
            "rubric": get_standard_rubric([
                {"category": "Explanation", "item": "Explains CPR involves rib fractures/trauma", "completed": False, "points": 1},
                {"category": "Success", "item": "Explains low success rate in frailty", "completed": False, "points": 1},
                {"category": "Focus", "item": "Emphasizes 'Medical Decision' not family burden", "completed": False, "points": 2},
                {"category": "Reassurance", "item": "Not 'giving up' (active care continues)", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Is it a family decision?", "model": "No, medical decision (but must consult)"}, {"q": "Form name?", "model": "DNACPR / ReSPECT"}]
        },
        {
            "id": "comm_couns_hiv",
            "name": "HIV Test Consent",
            "prompt": "You are Dave, 24. Here for a checkup. Doctor wants to do an HIV test. You are offended. 'Do I look like I have AIDS?'",
            "rubric": get_standard_rubric([
                {"category": "Normalization", "item": "'We test everyone' approach", "completed": False, "points": 1},
                {"category": "Benefits", "item": "Early treatment = Normal life", "completed": False, "points": 1},
                {"category": "Window", "item": "Explains window period", "completed": False, "points": 1},
                {"category": "Confidentiality", "item": "Reassures regarding data", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Consent reqs?", "model": "Verbal consent is sufficient"}, {"q": "U=U meaning?", "model": "Undetectable = Untransmittable"}]
        },
        {
            "id": "comm_angry",
            "name": "Angry Relative",
            "prompt": "You are Mr. Angry. Your mum has been in A&E for 6 hours waiting for a bed. No one has offered her tea. You are shouting.",
            "rubric": get_standard_rubric([
                {"category": "De-escalation", "item": "Calm voice/Listening", "completed": False, "points": 1},
                {"category": "Validation", "item": "Validates anger ('You are right to be upset')", "completed": False, "points": 2},
                {"category": "Action", "item": "Offers practical help (Tea/Update)", "completed": False, "points": 1},
                {"category": "Boundaries", "item": "Polite but firm if abusive", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Key strategy?", "model": "Listen, Validate, Act"}, {"q": "Safety?", "model": "Don't block exit, have chaperone if needed"}]
        },

        # --- ACUTE / EMERGENCY ---
        {
            "id": "acute_sepsis",
            "name": "Sepsis Six",
            "prompt": "You are Nurse. Patient is Mr. X, 60. Post-op bowel surgery. BP 85/50, HR 120, Temp 39. Confusion. Urine output low.",
            "rubric": get_standard_rubric([
                {"category": "Recog", "item": "Identifies Sepsis/Shock", "completed": False, "points": 1},
                {"category": "In 3", "item": "O2, Blood Cultures, IV Antibiotics", "completed": False, "points": 2},
                {"category": "Out 3", "item": "Lactate, Urine Output, IV Fluids", "completed": False, "points": 2},
                {"category": "Escalate", "item": "Call Senior/Outreach", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Sepsis 6 Timeframe?", "model": "Within 1 hour"}, {"q": "Fluid bolus?", "model": "500ml Crystalloid (Hartmann's/Saline) stat"}]
        },
        {
            "id": "acute_anaphylaxis",
            "name": "Anaphylaxis",
            "prompt": "You are a bystander. Your friend ate a nut. Lips swelling, wheezing, struggling to breathe. Pale and clammy.",
            "rubric": get_standard_rubric([
                {"category": "ABCDE", "item": "Airway/Breathing assessment", "completed": False, "points": 1},
                {"category": "Drug", "item": "IM Adrenaline (Epinephrine)", "completed": False, "points": 2},
                {"category": "Dose", "item": "500 micrograms (0.5ml 1:1000)", "completed": False, "points": 1},
                {"category": "Adjuvant", "item": "Chlorphenamine + Hydrocortisone", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Adrenaline dose (Adult)?", "model": "500mcg IM (1:1000)"}, {"q": "Refractory mechanism?", "model": "Repeat IM adrenaline q5min"}]
        },
        {
            "id": "acute_dka",
            "name": "DKA Management",
            "prompt": "You are Nurse. Patient (Type 1 Diabetic) is drowsy. Breath smells like pear drops. Vomiting. BM is 'High'.",
            "rubric": get_standard_rubric([
                {"category": "Recog", "item": "Diagnosis of DKA", "completed": False, "points": 1},
                {"category": "Fluids", "item": "IV Fluids (Aggressive rehydration)", "completed": False, "points": 1},
                {"category": "Insulin", "item": "Fixed Rate Insulin Infusion", "completed": False, "points": 1},
                {"category": "K+", "item": "Potassium replacement check", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Diagnostic Triad?", "model": "Hyperglycaemia, Ketosis, Acidosis"}, {"q": "Hypo risk?", "model": "Monitor Glucose hourly"}]
        },
        {
            "id": "acute_od",
            "name": "Paracetamol Overdose",
            "prompt": "You are Jen, 19. Took 'a packet' of paracetamol 4 hours ago after breakup. Feel fine. Regret it now.",
            "rubric": get_standard_rubric([
                {"category": "History", "item": "Time of ingestion (Staggered?)", "completed": False, "points": 1},
                {"category": "Dose", "item": "Weight (mg/kg calculation)", "completed": False, "points": 1},
                {"category": "Psych", "item": "Suicide intent assessment", "completed": False, "points": 1},
                {"category": "Plan", "item": "NAC (Parvolex) explanation", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "Treatment nomogram time?", "model": "4 hours post-ingestion levels"}, {"q": "Antidote?", "model": "N-acetylcysteine"}]
        },
        {
            "id": "acute_upper_airway",
            "name": "Choking (BLS)",
            "prompt": "Simulated scenario: Man in restaurant clutches throat, cannot speak or breathe. You must act.",
            "rubric": get_standard_rubric([
                {"category": "Assess", "item": "Encourage coughing first", "completed": False, "points": 1},
                {"category": "Action", "item": "5 Back Blows", "completed": False, "points": 1},
                {"category": "Action", "item": "5 Abdominal Thrusts", "completed": False, "points": 1},
                {"category": "Cycle", "item": "Repeat until clear or unconscious", "completed": False, "points": 1}
            ]),
            "viva": [{"q": "If unconscious?", "model": "Start CPR"}, {"q": "Complication of thrusts?", "model": "Visceral injury (Need surgical check)"}]
        }
    ]

    # Insert Data
    for s in stations_data:
        cursor.execute("INSERT INTO scenarios VALUES (?,?,?,?,?)", 
                       (s['id'], s['name'], s['prompt'], json.dumps(s['rubric']), json.dumps(s['viva'])))

    conn.commit()
    conn.close()
    print("✅ Database Synchronized: 50 Stations Loaded.")

if __name__ == "__main__":
    setup_database()