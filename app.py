from flask import Flask, render_template, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import json
import os
import requests

app = Flask(__name__)

# --- RATE LIMITER CONFIGURATION ---
# This identifies users by their IP address and stores counts in memory.
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per day", "20 per hour"],
    storage_uri="memory://",
)

# --- CONFIGURATION ---
API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_LOCAL_TESTING_KEY_HERE") 
# Updated to the latest stable Gemini 3 Flash for your 2026 build
MODEL = "gemini-3-flash" 
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"
WARDROBE_FILE = "wardrobe.json"

# --- DATABASE HELPERS ---
def load_wardrobe():
    default_structure = {"Tops": [], "Bottoms": [], "Shoes": [], "Accessories": []}
    if not os.path.exists(WARDROBE_FILE): return default_structure
    try:
        with open(WARDROBE_FILE, "r") as f:
            data = json.load(f)
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
@limiter.limit("3 per minute")  # Protects your API key from spamming
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

    Return ONLY JSON matching this format exactly:
    {{
      "best_outfit": "Detailed description",
      "color_palette": ["#HEXCODE1", "#HEXCODE2", "#HEXCODE3"],
      "why_it_works": "Reasoning",
      "perfume": "Fragrance suggestion",
      "skincare_tip": "Grooming tip"
    }}
    """

    result = call_ai(prompt)
    if not result:
        return jsonify({"error": "AI is thinking too hard. Try again!"})

    return jsonify(result)

# Error handler for when a user hits the rate limit
@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({"error": "Slow down, Rainmaker! You can only curate 3 looks per minute."}), 429

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)