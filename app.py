from flask import Flask, render_template, request
import google.generativeai as genai
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load API keys
tavily_api_key = os.getenv("TAVILY_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=gemini_api_key)

# Search and fetch college-related content
def fetch_college_info(query):
    headers = {
        "Authorization": f"Bearer {tavily_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query + " site:gcoeara.ac.in",
        "max_results": 5
    }
    response = requests.post("https://api.tavily.com/search", headers=headers, json=payload)
    results = response.json().get("results", [])
    full_content = "\n\n".join([r.get("content", "") for r in results])
    return full_content

# Gemini-based answer agent
def answer_agent(user_query):
    site_info = fetch_college_info(user_query)
    prompt = f"""
    You are an assistant that answers questions only about Government College of Engineering and Research, Avasari (GCOEARA). Use the following content extracted from the official college website to answer accurately.

    College Information:
    {site_info}

    User question: "{user_query}"

    Answer concisely and accurately.
    """
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = ""
    if request.method == 'POST':
        query = request.form['query']
        answer = answer_agent(query)

    return render_template("index.html", answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
