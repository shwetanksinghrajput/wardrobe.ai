import os
import json
from flask import Flask, render_template, request, jsonify
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
    return {"items": {}}

# --- THE LOGIC LAYER (Your Engineering Contribution) ---
def get_style_logic(skin_tone, occasion):
    """Hardcoded expert rules to guide the AI."""
    logic = {
        "fair": "Prioritize jewel tones (emerald, navy, ruby). Avoid pale yellows or neons that wash out the skin.",
        "olive": "Warm earth tones (terracotta, olive green, mustard) and gold accents work best.",
        "deep": "High-contrast colors like bright white, pastels, and bold primary colors are striking.",
        "medium": "Neutral tones, forest greens, and royal blues are highly recommended."
    }
    
    rules = logic.get(skin_tone.lower(), "Focus on high-contrast pairings and classic color theory.")
    
    if "wedding" in occasion.lower():
        rules += " Ensure the look is formal; no casual sneakers unless specified as 'beach wedding'."
        
    return rules

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-wardrobe', methods=['GET'])
def get_wardrobe():
    return jsonify(load_wardrobe())

@app.route('/save-wardrobe', methods=['POST'])
def save_wardrobe():
    data = request.json
    with open(WARDROBE_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({"status": "success"})

@app.route('/generate', methods=['POST'])
def generate():
    user_data = request.json
    wardrobe = load_wardrobe()
    
    # 1. Apply Local Logic Guardrails
    expert_rules = get_style_logic(user_data.get('skin_tone'), user_data.get('occasion'))
    
    # 2. Architect the Prompt
    prompt = f"""
    System: You are a professional high-end fashion stylist.
    User Profile: Skin Tone: {user_data.get('skin_tone')}, Body Type: {user_data.get('body_type')}, Vibe: {user_data.get('vibe')}.
    Context: Occasion: {user_data.get('occasion')}, Weather: {user_data.get('weather')}.
    Constraint Rules: {expert_rules}
    
    Available Wardrobe: {json.dumps(wardrobe['items'])}
    
    Task: Curate the best outfit. If the wardrobe is empty, suggest what they SHOULD buy.
    
    Return ONLY a JSON object with this exact structure:
    {{
      "best_outfit": "string",
      "why_it_works": "string",
      "color_palette": ["#hex1", "#hex2", "#hex3"],
      "perfume": "string",
      "skincare_tip": "string",
      "scores": {{
        "color_harmony": 1-10,
        "weather_suitability": 1-10,
        "occasion_fit": 1-10
      }}
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Clean the response text for any markdown formatting
        clean_text = response.text.replace('```json', '').replace('
```', '').strip()
        return jsonify(json.loads(clean_text))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))