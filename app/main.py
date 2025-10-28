import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Configuration:
# - Set GEMINI_API_KEY environment variable (or whichever LLM API key you use)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# Optional: override with full API URL via env var if you have one
GEMINI_API_URL = os.environ.get("GEMINI_API_URL") or "https://example-llm.api/endpoint"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini (LLM) API key not configured on server."}), 500

    payload_json = request.get_json() or {}
    text_to_analyze = payload_json.get("text_to_analyze", "").strip()
    if not text_to_analyze:
        return jsonify({"error": "No text provided for analysis."}), 400

    # System prompt
    system_prompt = (
        "You are a senior security analyst. Analyze the following text for security issues "
        "and return bullet points. Look for hardcoded secrets, SQL injection, XSS, insecure config, "
        "deprecated/unsafe APIs. If none found, say 'No issues found.'"
    )

    # Payload format is generic — adapt to the real Gemini API format you use.
    api_payload = {
        "system_prompt": system_prompt,
        "input": text_to_analyze,
        # include parameters if required by your LLM provider
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }

    try:
        resp = requests.post(GEMINI_API_URL, json=api_payload, headers=headers, timeout=20)
        resp.raise_for_status()
        result = resp.json()

        # The following parsing is generic — change according to your LLM's response shape.
        analysis_text = None
        if isinstance(result, dict):
            # common spots: 'analysis', 'output', 'choices', 'candidates'
            analysis_text = result.get("analysis") or result.get("output") or None
            if not analysis_text and "choices" in result and result["choices"]:
                choice = result["choices"][0]
                analysis_text = choice.get("text") or choice.get("message") or None
            if not analysis_text and "candidates" in result and result["candidates"]:
                cand = result["candidates"][0]
                if isinstance(cand, dict):
                    analysis_text = cand.get("content", {}).get("parts", [{}])[0].get("text")

        if not analysis_text:
            # as a fallback, just return the full JSON as a string (safe for debugging)
            return jsonify({"analysis": str(result)})

        return jsonify({"analysis": analysis_text})

    except requests.exceptions.RequestException as e:
        app.logger.exception("LLM API request failed")
        return jsonify({"error": f"Error communicating with LLM service: {e}"}), 503
    except Exception as e:
        app.logger.exception("Unexpected server error")
        return jsonify({"error": f"Unexpected error: {e}"}), 500


if __name__ == "__main__":
    # For simple local testing only. In production we run via Gunicorn (see Dockerfile).
    app.run(host="0.0.0.0", port=5000, debug=True)
