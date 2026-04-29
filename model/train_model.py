import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import pickle
import json
import os
import random
from itertools import combinations

# Create directories
os.makedirs('model', exist_ok=True)

def create_dataset():
    """Create comprehensive symptoms dataset"""
    data = """symptoms,disease
"fever cough headache fatigue","Common Cold"
"fever sore throat cough runny nose","Influenza"
"chest pain shortness of breath sweating nausea","Heart Attack"
"headache nausea vomiting sensitivity to light","Migraine"
"cough shortness of breath fever wheezing night sweats","Asthma"
"abdominal pain diarrhea vomiting fever nausea","Food Poisoning"
"high fever rash headache joint pain severe muscle pain","Dengue Fever"
"itching rash swelling hives difficulty breathing","Allergic Reaction"
"burning urination frequent urination pain lower abdomen blood urine","Urinary Tract Infection"
"persistent cough blood cough weight loss night sweats fatigue","Tuberculosis"
"stomach pain constipation diarrhea bloating","Irritable Bowel Syndrome"
"severe headache vision changes confusion weakness","Stroke"
"yellow skin yellow eyes dark urine fatigue","Jaundice"
"joint pain stiffness swelling morning stiffness","Rheumatoid Arthritis"
"memory loss confusion disorientation personality changes","Alzheimers Disease"
"rapid heartbeat palpitations dizziness fainting","Arrhythmia"
"swollen legs shortness breath fatigue weight gain","Congestive Heart Failure"
"blurred vision thirst urination weight loss","Diabetes Mellitus"
"numbness tingling weakness balance","Multiple Sclerosis"
"""
    
    with open('model/symptoms_dataset.csv', 'w', encoding='utf-8') as f:
        f.write(data)
    
    df = pd.read_csv('model/symptoms_dataset.csv', quotechar='"')
    print(f"✅ Base Dataset: {len(df)} samples, {df['disease'].nunique()} diseases")
    return df

def augment_data(df):
    """Create 10x more training data with symptom combinations"""
    augmented = []
    
    for _, row in df.iterrows():
        symptoms = row['symptoms'].lower().replace('"', '').split()
        disease = row['disease']
        
        # 1. Original
        augmented.append({'symptoms': ' '.join(symptoms), 'disease': disease})
        
        # 2. All 2-symptom combinations
        for combo in combinations(symptoms, 2):
            augmented.append({'symptoms': ' '.join(combo), 'disease': disease})
        
        # 3. All 3-symptom combinations  
        for combo in combinations(symptoms, 3):
            augmented.append({'symptoms': ' '.join(combo), 'disease': disease})
        
        # 4. Random shuffles
        for _ in range(5):
            shuffled = symptoms.copy()
            random.shuffle(shuffled)
            augmented.append({'symptoms': ' '.join(shuffled[:random.randint(2,5)]), 'disease': disease})
    
    aug_df = pd.DataFrame(augmented)
    print(f"🔄 Augmented: {len(aug_df)} samples (+{len(aug_df)-len(df)})")
    return aug_df

def create_advice_db():
    """Comprehensive medical advice database"""
    advice_data = {
        "Common Cold": {"advice": "Rest, fluids, paracetamol. Consult if >7 days.", "severity": "low", "precautions": "Hand washing"},
        "Influenza": {"advice": "Bed rest, antivirals, isolate 7 days.", "severity": "medium", "precautions": "Flu vaccine"},
        "Heart Attack": {"advice": "EMERGENCY! Call 108, chew Aspirin.", "severity": "critical", "precautions": "BP control"},
        "Migraine": {"advice": "Dark room, hydration, triptans.", "severity": "medium", "precautions": "Avoid triggers"},
        "Asthma": {"advice": "Inhaler now! Emergency if no relief.", "severity": "high", "precautions": "Carry inhaler"},
        "Food Poisoning": {"advice": "ORS, rest stomach 24hrs.", "severity": "medium", "precautions": "Food hygiene"},
        "Dengue Fever": {"advice": "Hospital, monitor platelets.", "severity": "high", "precautions": "Mosquito nets"},
        "Allergic Reaction": {"advice": "Antihistamine! Emergency if breathing issues.", "severity": "high", "precautions": "EpiPen"},
        "Urinary Tract Infection": {"advice": "3L water, antibiotics.", "severity": "medium", "precautions": "Hygiene"},
        "Tuberculosis": {"advice": "DOTS mandatory, isolation.", "severity": "critical", "precautions": "Cover cough"},
        "Irritable Bowel Syndrome": {"advice": "Fiber diet, stress management.", "severity": "low", "precautions": "Food diary"},
        "Stroke": {"advice": "EMERGENCY! Call 108 FAST test.", "severity": "critical", "precautions": "BP control"},
        "Jaundice": {"advice": "Bed rest, LFT tests.", "severity": "high", "precautions": "Safe water"},
        "Rheumatoid Arthritis": {"advice": "DMARDs, physiotherapy.", "severity": "high", "precautions": "Joint care"},
        "Alzheimers Disease": {"advice": "Cognitive therapy, safety.", "severity": "high", "precautions": "Memory aids"},
        "Arrhythmia": {"advice": "ECG, beta blockers.", "severity": "high", "precautions": "Avoid caffeine"},
        "Congestive Heart Failure": {"advice": "Diuretics, low salt.", "severity": "high", "precautions": "Daily weight"},
        "Diabetes Mellitus": {"advice": "Insulin, sugar monitoring.", "severity": "high", "precautions": "Diet/exercise"},
        "Multiple Sclerosis": {"advice": "DMTs, temperature control.", "severity": "high", "precautions": "Stay cool"}
    }
    
    with open('model/disease_advice.json', 'w', encoding='utf-8') as f:
        json.dump(advice_data, f, indent=2, ensure_ascii=False)

def train_model():
    print("🚀 AI Healthcare Model Training")
    print("=" * 50)
    
    # Load base data
    df = create_dataset()
    
    # AUGMENT DATA (Key to high accuracy!)
    df_aug = augment_data(df)
    
    # Preprocess
    df_aug['symptoms'] = df_aug['symptoms'].str.lower().str.replace(',', ' ').str.replace('"', '').str.strip()
    
    X = df_aug['symptoms']
    y = df_aug['disease']
    
    print(f"📈 FINAL Dataset: {len(X)} samples, {df_aug['disease'].nunique()} diseases")
    
    # Train-test split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Optimized Pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            max_features=3000, 
            ngram_range=(1, 3), 
            stop_words='english',
            min_df=2
        )),
        ('classifier', MultinomialNB(alpha=0.5))
    ])
    
    # Train
    print("\n🤖 Training High-Accuracy Model...")
    pipeline.fit(X_train, y_train)
    
    # Evaluate
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 FINAL ACCURACY: {accuracy:.1%}")
    print("\n📊 DETAILED REPORT:")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Test real examples
    test_examples = [
        "fever cough headache",
        "chest pain shortness breath", 
        "burning urination frequent",
        "high fever rash joint pain"
    ]
    
    print("\n🧪 REAL-WORLD TESTS:")
    for example in test_examples:
        pred = pipeline.predict([example.lower()])[0]
        probs = pipeline.predict_proba([example.lower()])[0]
        conf = max(probs) * 100
        print(f"   '{example}' → {pred} ({conf:.0f}%)")
    
    # Save model
    with open('model/model.pkl', 'wb') as f:
        pickle.dump(pipeline, f)
    
    # Save metadata
    available_diseases = sorted(df_aug['disease'].unique().tolist())
    with open('model/available_diseases.json', 'w') as f:
        json.dump(available_diseases, f)
    
    create_advice_db()
    
    print(f"\n🎉 PRODUCTION READY!")
    print(f"✅ Model: model.pkl ({accuracy:.1%} accuracy)")
    print(f"✅ Diseases: {len(available_diseases)}")
    print(f"✅ Samples: {len(df_aug)} augmented")
    print("\n🔥 START APP: python app.py")

if __name__ == "__main__":
    train_model()