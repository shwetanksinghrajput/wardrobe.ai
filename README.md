# Wardrobe AI: A Hybrid Logic Stylist

Wardrobe AI is a full-stack digital stylist that curates outfits from a user's personal collection. Moving beyond simple AI prompting, this project implements a **Hybrid Recommendation Engine** that combines hardcoded style logic with the creative synthesis of the Google Gemini Pro LLM.

## 🚀 Live Demo
**[Click here to view the live app on Render](https://wardrobe-ai-45ad.onrender.com)** *(Note: As this is hosted on a free tier, please allow ~40 seconds for the server to spin up on initial load.)*

## 📸 Project Preview
![Digital Closet & Stylist Input](sitpv1.png)
![AI Scoring & Strategic Reasoning](sitpv2.png)

---

## 🏗️ System Architecture & Engineering
This application was designed to solve the "Black Box" problem of generative AI by implementing a multi-layered logic flow:

1. **Rule-Based Logic Layer (Python):** Before inference, the system applies deterministic color theory and fashion guardrails (e.g., mapping skin tones to complementary palettes) to prevent AI hallucinations.
2. **Constraint-Based Inference:** The Gemini Pro model is utilized as a reasoning engine, processing the user's specific wardrobe JSON against real-time weather and occasion data.
3. **Quantitative Scoring Engine:** The output is evaluated on a 1-10 scale across three vectors: Color Harmony, Weather Suitability, and Occasion Fit, providing the user with data-driven confidence.

```mermaid
graph TD
    A[User Profile: Skin/Body/Vibe] --> B[Python Expert Rules]
    C[Environment: Weather/Occasion] --> B
    B -->|Logic Guardrails| D[Gemini Pro AI]
    E[Wardrobe Data Layer] --> D
    D --> F[Structured JSON Output]
    F --> G[Match Analysis UI]

    🛠️ Tech Stack
Backend: Python (Flask)

AI Inference: Google Gemini Pro API

Frontend: HTML5, CSS3 (Advanced Glassmorphism), JavaScript (ES6)

Data Persistence: JSON-based local storage

Deployment: CI/CD via GitHub & Render

🛡️ Security & Performance Optimization
1. Intelligent Rate Limiting
To protect the backend infrastructure and manage Google Gemini API quotas, Wardrobe.ai implements a sophisticated rate-limiting layer using Flask-Limiter.

Mechanism: IP-based tracking using the Fixed Window algorithm.

Thresholds: * 3 requests per minute for high-intensity AI generation.

100 requests per day global cap per user.

Purpose: Prevents server exhaustion from automated bot traffic and ensures the Free Tier API limits are not exceeded by individual users.

Graceful Degradation: Users who exceed the limit receive a custom HTTP 429 (Too Many Requests) response with a user-friendly instruction to wait for a cooldown period.

2. Efficient Resource Management
Persistent Storage: Uses a lightweight JSON-based database (wardrobe.json) to minimize redundant AI calls.

Contextual Prompting: Engineered to send only necessary wardrobe data, reducing token consumption and improving response latency.


🧠 Key Learnings
API Orchestration: Learning how to structure "System Prompts" to return strictly formatted JSON for frontend parsing.

UX/UI Design: Implementing "Glassmorphism" to create a premium, boutique-feel user experience.

Error Handling & Fallbacks: Developing Python-based expert rules to ensure stylistic accuracy even if AI creative output varies.

Developed by Shwetank Singh Rajput
