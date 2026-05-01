import os
import json
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# Setup Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

WARDROBE_FILE = 'wardrobe.json'

def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        with open(WARDROBE_FILE, 'r') as f:
            return json.load(f)
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    wardrobe = load_wardrobe()
    
    prompt = f"""
    User Profile:
    - Skin Tone: {data.get('skin_tone')}
    - Body Type: {data.get('body_type')}
    - Style Vibe: {data.get('vibe')}
    - Occasion: {data.get('occasion')}
    
    My Wardrobe: {json.dumps(wardrobe)}
    
    Instructions:
    Create a perfect outfit from my wardrobe. 
    Return ONLY a JSON object with these keys:
    'outfit' (description), 'why' (reasoning), 'grooming' (tips), 
    'score_color' (1-10), 'score_weather' (1-10), 'score_occasion' (1-10).
    """
    
    try:
        response = model.generate_content(prompt)
        # Fix for Line 89: Clean and partner all quotes correctly
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        result = json.loads(clean_text)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)}), 500

if __name__ == '__main__':
    # Professional Render Port Binding
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)