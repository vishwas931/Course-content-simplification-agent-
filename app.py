import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

load_dotenv()

app = Flask(__name__)

# ---------------------------------------------------------------------------
# watsonx.ai client setup
# ---------------------------------------------------------------------------

def get_model():
    """Create and return an IBM Granite model inference instance."""
    credentials = Credentials(
        url=os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com"),
        api_key=os.getenv("WATSONX_API_KEY"),
    )
    project_id = os.getenv("WATSONX_PROJECT_ID")

    params = {
        GenParams.MAX_NEW_TOKENS: 800,
        GenParams.MIN_NEW_TOKENS: 50,
        GenParams.TEMPERATURE: 0.7,
        GenParams.TOP_P: 0.9,
        GenParams.REPETITION_PENALTY: 1.1,
    }

    model = ModelInference(
        model_id="ibm/granite-4-h-small",
        credentials=credentials,
        project_id=project_id,
        params=params,
    )
    return model


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

LEVEL_DESCRIPTIONS = {
    "Beginner":     "a complete beginner with no prior knowledge. Use very simple words, short sentences, and everyday analogies.",
    "Intermediate": "a learner with some background knowledge. Use clear explanations with moderate technical terms defined briefly.",
    "Advanced":     "an advanced learner or professional. Use precise technical language and assume strong prior knowledge.",
}

def build_prompt(content: str, level: str) -> str:
    description = LEVEL_DESCRIPTIONS.get(level, LEVEL_DESCRIPTIONS["Intermediate"])
    prompt = f"""You are a helpful academic tutor. Rewrite the following course content for {description}

Return your response using exactly these three section headers (keep the headers as written):

SIMPLIFIED EXPLANATION:
<rewrite the content clearly for the learner level>

KEY POINTS:
- <key point 1>
- <key point 2>
- <key point 3>

SHORT EXAMPLE:
<one short, concrete real-world example that illustrates the concept>

Course content to simplify:
{content.strip()}

Response:"""
    return prompt


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------

def parse_response(text: str) -> dict:
    """Extract the three sections from the model's response text."""
    sections = {
        "simplified": "",
        "key_points": "",
        "example": "",
    }

    # Extract SIMPLIFIED EXPLANATION
    match = re.search(
        r"SIMPLIFIED EXPLANATION:\s*(.*?)(?=KEY POINTS:|SHORT EXAMPLE:|$)",
        text, re.DOTALL | re.IGNORECASE
    )
    if match:
        sections["simplified"] = match.group(1).strip()

    # Extract KEY POINTS
    match = re.search(
        r"KEY POINTS:\s*(.*?)(?=SHORT EXAMPLE:|$)",
        text, re.DOTALL | re.IGNORECASE
    )
    if match:
        sections["key_points"] = match.group(1).strip()

    # Extract SHORT EXAMPLE
    match = re.search(
        r"SHORT EXAMPLE:\s*(.*?)$",
        text, re.DOTALL | re.IGNORECASE
    )
    if match:
        sections["example"] = match.group(1).strip()

    # Fallback: if parsing failed, return the full text as simplified
    if not sections["simplified"] and not sections["key_points"]:
        sections["simplified"] = text.strip()

    return sections


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/simplify", methods=["POST"])
def simplify():
    data = request.get_json()
    content = (data.get("content") or "").strip()
    level = (data.get("level") or "Beginner").strip()

    if not content:
        return jsonify({"error": "Please paste some course content first."}), 400

    if level not in LEVEL_DESCRIPTIONS:
        return jsonify({"error": "Invalid level. Choose Beginner, Intermediate, or Advanced."}), 400

    # Check credentials are configured
    if not os.getenv("WATSONX_API_KEY") or os.getenv("WATSONX_API_KEY") == "your_ibm_cloud_api_key_here":
        return jsonify({"error": "WATSONX_API_KEY is not configured in your .env file."}), 500
    if not os.getenv("WATSONX_PROJECT_ID") or os.getenv("WATSONX_PROJECT_ID") == "your_watsonx_project_id_here":
        return jsonify({"error": "WATSONX_PROJECT_ID is not configured in your .env file."}), 500

    try:
        model = get_model()
        prompt = build_prompt(content, level)
        response = model.generate_text(prompt=prompt)
        result = parse_response(response)
        return jsonify(result)

    except Exception as e:
        error_msg = str(e)
        # Give a friendlier message for common auth errors
        if "401" in error_msg or "Unauthorized" in error_msg:
            error_msg = "Authentication failed. Check your WATSONX_API_KEY in .env."
        elif "404" in error_msg or "not found" in error_msg.lower():
            error_msg = "Model or project not found. Check your WATSONX_PROJECT_ID and WATSONX_URL in .env."
        return jsonify({"error": f"API error: {error_msg}"}), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
