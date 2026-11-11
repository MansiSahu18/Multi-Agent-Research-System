<p align="center">
  <h1 align="center">🔬 ResearchMind</h1>
  <p align="center">
    <strong>An Autonomous Multi-Agent AI Research Platform</strong>
    <br />
    <a href="#features">Features</a>
    ·
    <a href="#architecture">Architecture</a>
    ·
    <a href="#installation">Installation</a>
    ·
    <a href="#usage">Usage</a>
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Framework-LangChain-green.svg" alt="LangChain">
  <img src="https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg" alt="Streamlit">
  <img src="https://img.shields.io/badge/Database-ChromaDB-orange.svg" alt="ChromaDB">
  <img src="https://img.shields.io/badge/LLMs-OpenRouter-black.svg" alt="OpenRouter">
</p>

---

## 📖 Overview

**ResearchMind** is an advanced, end-to-end AI research orchestration system. It moves beyond simple LLM wrappers by employing a **multi-agent architecture** to autonomously search the web, scrape technical data, verify facts, and synthesize comprehensive Markdown reports. 

Designed for accuracy and transparency, ResearchMind features a **Human-in-the-Loop (HITL)** checkpoint, persistent vector memory (RAG), and a self-reflecting "Critic" agent to eliminate hallucinations and ensure high-fidelity outputs.

---

## ✨ Key Features

- **🤖 Multi-Agent Orchestration:** Four distinct LangChain agents (Search, Scrape, Writer, Critic) collaborate seamlessly to handle complex research tasks.
- **🧠 Persistent Vector Memory (RAG):** Integrates ChromaDB to remember past research. If a topic is searched twice, the system retrieves it from memory instantly—saving time and API costs.
- **🛑 Human-in-the-Loop (HITL):** A built-in pause mechanism allows users to review, edit, and prune scraped web context *before* the LLM generates the final report.
- **🧐 Critic-in-the-Loop:** An automated peer-review agent evaluates the final draft for bias, formatting, and factual consistency.
- **🌊 Token-Level Streaming:** Watch the Writer agent draft your report in real-time within the UI.
- **🌐 Provider-Agnostic:** Powered by OpenRouter, allowing seamless switching between OpenAI, Anthropic (Claude), and Meta (Llama) models without changing core logic.
- **💎 Glassmorphism UI:** A sleek, responsive custom frontend built with Streamlit and custom CSS.

---

## 🏗️ System Architecture

The pipeline follows a linear orchestration flow with a feedback loop and human intervention checkpoint:

1. **Memory Check (ChromaDB):** System converts the query to vectors and checks local memory. If a match is found, skip to Step 4.
2. **Search Agent:** Uses web search tools to identify the most recent and authoritative live web sources.
3. **Reader Agent:** Visits identified URLs and scrapes the deep text, filtering out noise and ads.
4. **Human Review (HITL):** The UI pauses. The user reviews and edits the scraped context.
5. **Writer Agent:** Synthesizes the approved context into a structured, highly detailed Markdown report (streamed to the UI).
6. **Critic Agent:** Reviews the report and appends an evaluation scorecard.

---

## 🛠️ Tech Stack

* **Backend Orchestration:** `LangChain`, `Python`
* **Large Language Models:** `OpenRouter API` (Claude 3.5 Sonnet, GPT-4o, etc.)
* **Vector Database & Embeddings:** `ChromaDB`, `OpenAIEmbeddings`
* **Web Scraping:** `BeautifulSoup4`, `Requests`
* **Frontend:** `Streamlit` (with custom CSS/Glassmorphism)

---

## 🚀 Installation & Setup

### Prerequisites
* Python 3.11
* An [OpenRouter API Key](https://openrouter.ai/) (and optionally, a Search API key like Tavily or DuckDuckGo depending on your agent setup).

* 2. Create a virtual environment
It is recommended to use a virtual environment to manage dependencies and avoid conflicts.

# Create the environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
3. Install dependencies
Once the virtual environment is active, install all required Python packages.

pip install -r requirements.txt
4. Set up environment variables
Create a file named .env in the root directory of the project to store your sensitive API keys.

Code snippet
OPENROUTER_API_KEY=your_openrouter_api_key_here
# Add any other required API keys here (e.g., TAVILY_API_KEY)
5. Run the application
Launch the Streamlit dashboard to start using ResearchMind.


 streamlit run app.py



