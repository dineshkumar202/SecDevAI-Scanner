import os
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- THIS IS THE CRITICAL PART ---
# Get the API key from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# This is the REAL API URL, not 'example-llm.api'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"
# --- END CRITICAL PART ---

@app.route('/')
def index():
    """Renders the main homepage."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handles the analysis request from the frontend."""
    if not GEMINI_API_KEY:
        return jsonify({"error": "Gemini API key is not configured on the server."}), 500

    try:
        # Get the text to analyze from the request
        text_to_analyze = request.json.get('text_to_analyze')
        if not text_to_analyze:
            return jsonify({"error": "No text provided for analysis."}), 400

        # Define the system prompt for the AI
        system_prompt = (
            "You are a senior security analyst. Your task is to analyze the following text "
            "for any potential security vulnerabilities, flaws, or bad practices. "
            "Look for things like: \n"
            "- Hardcoded secrets (API keys, passwords, private keys)\n"
            "- SQL injection vulnerabilities\n"
            "- Cross-Site Scripting (XSS) vulnerabilities\n"
            "- Insecure configurations or logic\n"
            "- Deprecated or unsafe functions\n"
            "Provide a concise, bullet-pointed summary of your findings. "
            "If no issues are found, state that clearly."
        )

        # Construct the payload for the Gemini API
        payload = {
            "contents": [
                {
                    "parts": [{"text": text_to_analyze}]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            }
        }

        # Make the API call to the REAL URL
        response = requests.post(API_URL, json=payload, headers={'Content-Type': 'application/json'})
        
        response.raise_for_status() # Raise an exception for bad status codes
        
        result = response.json()
        
        # Extract the generated text from the AI's response
        if (
            "candidates" in result and
            result["candidates"] and
            "content" in result["candidates"][0] and
            "parts" in result["candidates"][0]["content"] and
            result["candidates"][0]["content"]["parts"]
        ):
            analysis_text = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"analysis": analysis_text})
        else:
            # Handle cases where the API response is not as expected
            print("Unexpected API response structure:", result)
            return jsonify({"error": "Failed to parse analysis from API response."}), 500

    except requests.exceptions.RequestException as e:
        # Handle network errors or bad HTTP responses
        print(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Error communicating with AI service: {e}"}), 503
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

