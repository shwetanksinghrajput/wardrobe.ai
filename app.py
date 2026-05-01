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
    Return ONLY raw JSON. No markdown, no 'here is your outfit', no preamble.
    WARDROBE: {json.dumps(wardrobe)}
    OCCASION: {data.get('occasion')}
    TASK: Suggest an outfit from the wardrobe.
    JSON structure: 
    {{"outfit": "...", "why": "...", "grooming": "...", "score_color": 10, "score_weather": 10, "score_occasion": 10}}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # LOG THE RAW RESPONSE: This lets us see exactly what Gemini said in Render Logs
        print(f"RAW AI RESPONSE: {raw_text}")

        # Aggressive cleaning
        cleaned_text = raw_text.replace('```json', '').replace('```', '').strip()
        
        # Find the first '{' and last '}' just in case there's extra text
        start = cleaned_text.find('{')
        end = cleaned_text.rfind('}') + 1
        if start != -1 and end != 0:
            cleaned_text = cleaned_text[start:end]

        result = json.loads(cleaned_text)
        return json.dumps(result)
        
    except Exception as e:
        print(f"PARSING ERROR: {str(e)}")
        return json.dumps({
            "outfit": f"AI Error: {str(e)[:50]}",
            "why": "Check Render logs for 'RAW AI RESPONSE'.",
            "grooming": "Parsing failed.",
            "score_color": 0, "score_weather": 0, "score_occasion": 0
        })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)