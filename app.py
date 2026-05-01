import os
import json
import traceback
from flask import Flask, render_template, request
import google.generativeai as genai

app = Flask(__name__)

# Setup Gemini - Using 'gemini-pro' for guaranteed Free Tier stability
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

WARDROBE_FILE = 'wardrobe.json'

def load_wardrobe():
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"DEBUG: Wardrobe load error: {e}")
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
    
    # Strict prompt to force clean JSON
    prompt = f"""
    Return ONLY raw JSON. No markdown, no intro.
    USER: Skin {data.get('skin_tone')}, Body {data.get('body_type')}, Vibe {data.get('vibe')}.
    CONTEXT: {data.get('occasion')} in {data.get('weather')}.
    WARDROBE: {json.dumps(wardrobe)}
    
    JSON FORMAT:
    {{
        "outfit": "description",
        "why": "reasoning",
        "grooming": "tip",
        "score_color": 10,
        "score_weather": 10,
        "score_occasion": 10
    }}
    """
    
    try:
        print("DEBUG: Sending request to Gemini...")
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # This will show up in your Render Logs so we can see the "Look"
        print(f"DEBUG: AI RESPONSE: {raw_text}")
        
        # Extract JSON if Gemini adds backticks or chatter
        if "{" in raw_text:
            cleaned_text = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
        else:
            cleaned_text = raw_text
            
        result = json.loads(cleaned_text)
        return json.dumps(result)
        
    except Exception as e:
        # Full error reporting
        error_msg = str(e)
        print(f"DEBUG: ERROR OCCURRED: {error_msg}")
        print(traceback.format_exc())
        
        return json.dumps({
            "outfit": f"Technical Issue: {error_msg[:50]}",
            "why": "Check Render logs for the full DEBUG message.",
            "grooming": "Please refresh and try again.",
            "score_color": 0, "score_weather": 0, "score_occasion": 0
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)