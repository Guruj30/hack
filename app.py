from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# --- CONFIGURATION (Add your keys here) ---
GROK_API_KEY = "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"
#HF_API_KEY = "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"

HF_API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

# --- OFFLINE LOGIC FUNCTION ---
def calculate_triage(age, symptoms, days):
    risk_score = 0
    high_risk = ["chest pain", "difficulty breathing", "severe fever", "high fever", "seizure"] # Add more from your list
    moderate = ["fever", "cough", "vomiting", "diarrhea", "stomach ache"]
    mild = ["cold", "runny nose", "sneezing", "mild headache"]

    # Simple logic based on your code
    for s in [s.strip().lower() for s in symptoms.split(",")]:
        if s in high_risk: risk_score += 5
        elif s in moderate: risk_score += 3
        elif s in mild: risk_score += 1
        else: risk_score += 2
    
    if int(age) < 5 or int(age) > 60: risk_score += 2
    if int(days) >= 7: risk_score += 4
    
    if risk_score >= 9: return "red"
    elif risk_score >= 5: return "yellow"
    else: return "green"

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/online', methods=['GET', 'POST'])
@app.route('/online', methods=['GET', 'POST'])
def online():
    if request.method == 'POST':
        # Use .get(key, default) to prevent the "BadRequestKeyError"
        age = request.form.get('age', 0)
        symptoms = request.form.get('symptoms', '')
        
        # We manually set days to 0 because it's not in the online form
        days = 0 
        
        # Now call your function with the default days
        triage = calculate_triage(age, symptoms, days)
        return redirect(url_for(triage))
    
    return render_template('online.html')

@app.route('/offline', methods=['GET', 'POST'])
def offline():
    if request.method == 'POST':
        age = request.form.get('age')
        symptoms = request.form.get('symptoms')
        
        
        
        result_color = calculate_triage(age, symptoms)
        return redirect(url_for(result_color))
    return render_template('offline.html')

# Result Pages
@app.route('/red')
def red(): return render_template('red.html')

@app.route('/yellow')
def yellow(): return render_template('yellow.html')

@app.route('/green')
def green(): return render_template('green.html')

# --- CHATBOT (Hugging Face) ---
@app.route('/chat', methods=['GET', 'POST'])
def chat():
    bot_response = ""
    if request.method == 'POST':
        user_message = request.form.get('message')
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {"inputs": user_message}
        

        response = requests.post(HF_API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            bot_response = response.json()[0].get('generated_text', "I'm a bit sleepy, try again!")
        else:
            bot_response = "Error connecting to AI. Check your API Key."
            
    return render_template('chat.html', response=bot_response)

if __name__ == '__main__':
    app.run(debug=True)