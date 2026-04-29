from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import json
import re
from collections import Counter
import os
import requests as http_requests
import csv
from datetime import datetime

app = Flask(__name__)


# Load trained model and data
with open('model/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('model/disease_advice.json', 'r', encoding='utf-8') as f:
    disease_advice = json.load(f)

with open('model/available_diseases.json', 'r') as f:
    available_diseases = json.load(f)

# Language translation mappings
LANGUAGE_MAP = {
    'en': 'English',
    'kn': 'Kannada',
    'hi': 'Hindi',
    'ta': 'Tamil',
    'te': 'Telugu',
    'mr': 'Marathi',
    'ml': 'Malayalam'
}

def translate_to_english(text, lang):
    """Translate any language to English using MyMemory free API"""
    if lang == 'en':
        return text
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {'q': text, 'langpair': f'{lang}|en'}
        res = http_requests.get(url, params=params, timeout=5)
        result = res.json()
        return result['responseData']['translatedText']
    except:
        return text  # fallback to original if translation fails

def translate_disease_name(disease, lang):
    """Translate disease name to selected language using MyMemory free API"""
    if lang == 'en':
        return disease
    try:
        url = "https://api.mymemory.translated.net/get"
        params = {'q': disease, 'langpair': f'en|{lang}'}
        res = http_requests.get(url, params=params, timeout=5)
        result = res.json()
        return result['responseData']['translatedText']
    except:
        return disease  # fallback to English if translation fails

def preprocess_symptoms(symptoms_text):
    """Clean and preprocess symptoms text"""
    symptoms = re.findall(r'\b\w+\b', symptoms_text.lower())
    return ' '.join(symptoms)

@app.route('/')
def index():
    return render_template('index.html', languages=LANGUAGE_MAP)

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() or {}
        symptoms = data.get('symptoms', 'fever').strip()
        lang = data.get('language', 'en')

        # Translate symptoms to English for model
        english_symptoms = translate_to_english(symptoms, lang)

        # ULTRA-FAST PROCESSING
        processed = re.sub(r'[^a-zA-Z\s]', ' ', english_symptoms.lower())
        words = [w for w in processed.split() if len(w) > 2]
        if len(words) < 2:
            words = ['fever', 'cough']  # Fallback

        processed_text = ' '.join(words[:10])  # Max 10 words

        # PREDICT (cached = instant)
        prediction = model.predict([processed_text])[0]
        probs = model.predict_proba([processed_text])[0]
        confidence = max(probs) * 100

        advice_data = disease_advice.get(prediction, {
            'advice': {'en': 'Consult a doctor immediately.'},
            'severity': 'medium',
            'precautions': {'en': 'Seek medical help.'}
        })

        # Pick correct language from JSON, fallback to English
        advice = advice_data['advice'].get(lang, advice_data['advice'].get('en', 'Consult a doctor.'))
        precautions = advice_data.get('precautions', {}).get(lang, advice_data.get('precautions', {}).get('en', ''))

        # Translate disease name to selected language
        translated_disease = translate_disease_name(prediction, lang)

        return jsonify({
            'success': True,
            'disease': translated_disease,
            'confidence': round(confidence, 1),
            'advice': advice,
            'severity': advice_data['severity'],
            'precautions': precautions
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'diseases': len(available_diseases)})

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'API Working!',
        'model_loaded': model is not None,
        'diseases': len(available_diseases) if 'available_diseases' in globals() else 0
    })

@app.route('/auth')
def auth():
    return render_template('auth.html')

import csv
from datetime import datetime

@app.route('/api/save-user', methods=['POST'])
def save_user():
    try:
        data = request.get_json() or {}
        
        csv_file = 'user_data.csv'
        file_exists = os.path.isfile(csv_file)
        
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = [
                'firstName', 'lastName', 'email', 'phone',
                'age', 'gender', 'location', 'deviceId',
                'ipAddress', 'registeredAt', 'sessionStart'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'firstName': data.get('firstName', ''),
                'lastName': data.get('lastName', ''),
                'email': data.get('email', ''),
                'phone': data.get('phone', ''),
                'age': data.get('age', ''),
                'gender': data.get('gender', ''),
                'location': data.get('location', ''),
                'deviceId': data.get('deviceId', ''),
                'ipAddress': data.get('ipAddress', ''),
                'registeredAt': data.get('registeredAt', ''),
                'sessionStart': datetime.now().isoformat()
            })
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
        @app.route('/api/test-csv')
        def test_csv():
            try:
                csv_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_data.csv')
                file_exists = os.path.isfile(csv_file)
                
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    fieldnames = ['firstName', 'lastName', 'email', 'phone', 'age', 'gender', 'location', 'deviceId', 'ipAddress', 'registeredAt', 'sessionStart']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if not file_exists:
                        writer.writeheader()
                    writer.writerow({
                        'firstName': 'Sushma ',
                        'lastName': 'Joshi',
                        'email': 'sushma.sj29@gmail.com',
                        'phone': '+91 9019739656',
                        'age': '22',
                        'gender': 'female',
                        'location': 'Hubli, Karnataka',
                        'deviceId': 'test_device_123',
                        'ipAddress': '127.0.0.1',
                        'registeredAt': datetime.now().isoformat(),
                        'sessionStart': datetime.now().isoformat()
                    })
                return jsonify({'success': True, 'csv_path': csv_file})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)