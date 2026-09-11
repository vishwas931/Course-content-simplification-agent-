# Course Content Simplifier

**AICTE 2026 — Problem Statement 19**

A minimal Flask web application that takes academic course content and a learner proficiency level (Beginner, Intermediate, Advanced) and uses IBM Granite via IBM watsonx.ai to rewrite the content at the selected level, along with key points and a short example.

---

## Project Structure

```
Course_Content_Simplifier/
├── app.py                  ← Flask server + watsonx.ai API integration
├── .env                    ← Your IBM credentials (never share/commit this)
├── .env.example            ← Credential template
├── requirements.txt        ← Python dependencies
├── templates/
│   └── index.html          ← Single-page web UI
└── README.md               ← This file
```

---

## Prerequisites

- Python 3.9 or higher
- An IBM Cloud account
- A watsonx.ai project created on IBM Cloud

---

## IBM Cloud Setup

### Step 1 — Get your IBM Cloud API Key
1. Log in to [https://cloud.ibm.com](https://cloud.ibm.com)
2. Go to **Manage → Access (IAM) → API Keys**
3. Click **Create an IBM Cloud API key**
4. Copy the key immediately (it is only shown once)

### Step 2 — Get your watsonx.ai Project ID
1. Go to [https://dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)
2. Open your project (or create one: **New project → Create an empty project**)
3. Go to **Manage → General**
4. Copy the **Project ID** shown at the top

### Step 3 — Associate a Watson Machine Learning service
Your watsonx.ai project must have a **Watson Machine Learning** service instance associated:
1. In your project, go to **Manage → Services & integrations**
2. Click **Associate service → Watson Machine Learning**
3. If you don't have one, create a free Lite instance first at [https://cloud.ibm.com/catalog/services/watson-machine-learning](https://cloud.ibm.com/catalog/services/watson-machine-learning)

---

## Local Setup & Configuration

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure credentials

Copy `.env.example` to `.env`:

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Open `.env` and fill in your values:

```env
WATSONX_API_KEY=your_actual_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

> **Region note:** Use `us-south` if your IBM Cloud account was created in Dallas (the most common default). Change to `eu-de`, `eu-gb`, or `jp-tok` if your resources are in a different region.

---

## Running the Application

```bash
python app.py
```

Open your browser at: **http://localhost:5000**

You should see the Course Content Simplifier UI.

---

## Testing the Application

### Quick test content (paste into the text box):

**Test 1 — Computer Science concept:**
```
A binary search tree (BST) is a rooted binary tree data structure where each 
node stores a key greater than all keys in its left subtree and less than all 
keys in its right subtree. This property enables efficient searching, insertion, 
and deletion operations with an average time complexity of O(log n).
```

**Test 2 — Physics concept:**
```
Newton's second law of motion states that the rate of change of momentum of 
a body is directly proportional to the net force applied to it and occurs in 
the direction of the applied force. Mathematically expressed as F = ma, where 
F is force in Newtons, m is mass in kilograms, and a is acceleration in m/s².
```

### Expected output per run:
- **Simplified Explanation** — The concept rewritten for the selected level
- **Key Points** — 3–4 bullet points summarising the core ideas
- **Short Example** — One concrete real-world example

### Test all three levels:
Run the same content at Beginner, Intermediate, and Advanced to see how the output changes — this is a great demo screenshot sequence.

---

## Troubleshooting

| Error | Fix |
|---|---|
| `WATSONX_API_KEY is not configured` | Open `.env` and add your API key |
| `Authentication failed` | Double-check the API key is correct and active |
| `Model or project not found` | Verify `WATSONX_PROJECT_ID` and `WATSONX_URL` region |
| `No module named flask` | Run `pip install -r requirements.txt` with venv activated |
| `Address already in use` | Another app is on port 5000; edit `app.py` last line to use port 5001 |

---

## Model Used

**`ibm/granite-3-8b-instruct`** — IBM Granite 3 instruction-tuned model available on watsonx.ai. No special activation is required; it is accessible to all watsonx.ai projects with an associated Watson Machine Learning instance.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| `flask` | 3.0.3 | Web server |
| `ibm-watsonx-ai` | 1.1.2 | IBM Granite / watsonx.ai SDK |
| `python-dotenv` | 1.0.1 | Load `.env` credentials |
