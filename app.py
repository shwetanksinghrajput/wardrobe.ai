from flask import Flask, render_template, request, jsonify
import json
import os
import requests

app = Flask(__name__)

# --- CONFIGURATION ---
# Replace Plan B with your real AIzaSy... key for local testing.
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_LOCAL_TESTING_KEY_HERE") 
MODEL = "gemini-3-flash-preview"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
WARDROBE_FILE = "wardrobe.json"

# --- DATABASE HELPERS ---
def load_wardrobe():
    default_structure = {"Tops": [], "Bottoms": [], "Shoes": [], "Accessories": []}
    if not os.path.exists(WARDROBE_FILE): return default_structure
    try:
        with open(WARDROBE_FILE, "r") as f:
            data = json.load(f)
            # Migration: If it's the old flat list, put everything in 'Tops'
            if isinstance(data.get("items"), list):
                old_list = data.get("items", [])
                return {"Tops": old_list, "Bottoms": [], "Shoes": [], "Accessories": []}
            return data.get("items", default_structure)
    except:
        return default_structure

def save_wardrobe(items):
    with open(WARDROBE_FILE, "w") as f: json.dump({"items": items}, f)

# --- AI HELPER ---
def call_ai(prompt):
    try:
        response = requests.post(
            URL,
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"response_mime_type": "application/json"} 
            },
            timeout=25
        )
        data = response.json()
        if "error" in data:
            print("API Error:", data["error"])
            return None
            
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip().replace("```json", "").replace("```", "")
        return json.loads(text)
    except Exception as e:
        print("AI Request Failed:", e)
        return None

# --- WEB ROUTES ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get-wardrobe", methods=["GET"])
def get_wardrobe_api():
    return jsonify({"items": load_wardrobe()})

@app.route("/save-wardrobe", methods=["POST"])
def save_wardrobe_api():
    items = request.json.get("items", {})
    save_wardrobe(items)
    return jsonify({"status": "Success"})

@app.route("/generate", methods=["POST"])
def generate_style():
    data = request.json
    wardrobe_dict = load_wardrobe()
    
    is_empty = all(len(items) == 0 for items in wardrobe_dict.values())
    if is_empty:
        return jsonify({"error": "Your closet is empty. Add some clothes first!"})

    wardrobe_text = ""
    for category, items in wardrobe_dict.items():
        if items: wardrobe_text += f"{category}: {', '.join(items)}. "

    occasion = data.get("occasion", "Casual hanging out")
    weather = data.get("weather", "Mild")
    skin_tone = data.get("skin_tone", "Olive")
    body_type = data.get("body_type", "Athletic")
    vibe = data.get("vibe", "Old Money")

    prompt = f"""
    You are a high-end men's fashion stylist.
    Wardrobe: {wardrobe_text}
    Occasion: {occasion}
    Weather: {weather}
    User profile -> Skin tone: {skin_tone}, Body Type: {body_type}, Style vibe: {vibe}

    Return ONLY JSON matching this format exactly. DO NOT use markdown, just raw JSON:
    {{
      "best_outfit": "Detailed description of the best outfit combination",
      "color_palette": ["#HEXCODE1", "#HEXCODE2", "#HEXCODE3"],
      "why_it_works": "Why these colors match the skin tone and occasion",
      "perfume": "Fragrance type suggestion",
      "skincare_tip": "One quick grooming/skincare tip"
    }}
    Rules: 
    - Use ONLY items from the provided Wardrobe for the outfit.
    - color_palette MUST contain exactly 3 or 4 valid hex color codes representing the outfit (e.g., ["#000080", "#F5F5DC", "#FFFFFF"]). Do not leave this empty.
    """

    result = call_ai(prompt)
    
    if not result:
        return jsonify({"error": "AI is thinking too hard. Try again!"})

    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)