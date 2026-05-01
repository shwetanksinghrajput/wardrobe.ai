import os
import json
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# Setup Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

WARDROBE_FILE = 'wardrobe.json'

def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-wardrobe')
def get_wardrobe():
    return json.dumps(load_wardrobe())

@app.route('/save-wardrobe', methods=['POST'])
def save_wardrobe():
    data = request.json
    with open(WARDROBE_FILE, 'w') as f:
        json.dump(data, f)
    return json.dumps({"status": "success"})

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    wardrobe = load_wardrobe()
    
    prompt = f"""
    User Profile: Skin {data.get('skin_tone')}, Body {data.get('body_type')}, Vibe {data.get('vibe')}.
    Occasion: {data.get('occasion')}, Weather: {data.get('weather')}.
    Wardrobe Items: {json.dumps(wardrobe)}
    
    TASK: Create a professional outfit using the items above.
    REQUIRED JSON FORMAT (Return ONLY raw JSON, no extra text):
    {{
        "outfit": "detailed description of the outfit",
        "why": "strategic reasoning for these choices",
        "grooming": "specific grooming or accessory tip",
        "score_color": 9,
        "score_weather": 8,
        "score_occasion": 9
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Line 89 FIX: Clean up markdown and extra quotes
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()
            
        result = json.loads(text)
        return json.dumps(result)
        
    except Exception as e:
        # Emergency Fallback so UI never shows "undefined"
        return json.dumps({
            "outfit": "A classic ensemble featuring your favorite pieces.",
            "why": "Standard stylistic principles of color coordination.",
            "grooming": "Maintain a clean, polished look for the occasion.",
            "score_color": 8, "score_weather": 8, "score_occasion": 8
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)