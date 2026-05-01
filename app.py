import os
import json
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# Setup Gemini - Using 'gemini-pro' for maximum compatibility on Free Tier
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

WARDROBE_FILE = 'wardrobe.json'

def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
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
    
    # Precise instructions to force the AI to behave
    prompt = f"""
    Return ONLY raw JSON. No conversational filler.
    USER: Skin {data.get('skin_tone')}, Body {data.get('body_type')}, Vibe {data.get('vibe')}.
    CONTEXT: {data.get('occasion')} in {data.get('weather')}.
    WARDROBE: {json.dumps(wardrobe)}
    
    TASK: Pick a specific outfit from the items above.
    JSON FORMAT:
    {{
        "outfit": "description of look",
        "why": "strategic reasoning",
        "grooming": "grooming tip",
        "score_color": 9,
        "score_weather": 9,
        "score_occasion": 9
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # JSON REPAIR: Strips away any extra text Gemini might add
        if "{" in text:
            text = text[text.find("{"):text.rfind("}")+1]
            
        result = json.loads(text)
        return json.dumps(result)
        
    except Exception as e:
        # Fallback if the AI is slow or the parsing hits a snag
        return json.dumps({
            "outfit": "Stylist is matching your collection...",
            "why": "Optimizing for color theory and occasion context.",
            "grooming": "Maintain a clean aesthetic.",
            "score_color": 8, "score_weather": 8, "score_occasion": 8
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)