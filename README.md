# 🔎 ReAct Agent

An autonomous AI research agent built on the **ReAct (Reason + Act)** pattern — it thinks before it acts, deciding on its own what to search for, reading live results from the web, and refining its approach until it's confident enough to answer.

**Live demo:** _add your Streamlit Cloud link here_

## What it does

- Takes a question that needs current, real-world information (not fixed knowledge)
- Reasons step by step: decides whether it needs to search, what to search for, and when it has enough information
- Searches the live web (DuckDuckGo) and reads real results — not a static knowledge base
- Loops up to 4 times, refining its search if the first attempt isn't enough
- Answers only using what it actually found, with every answer backed by cited sources
- Shows its full reasoning trace (Thought → Search → Thought → ... → Answer) for every question, so the decision-making process is never hidden

## Why this is different from a RAG system

A RAG system retrieves from a fixed, pre-built knowledge base. This agent has no fixed knowledge base at all — it decides for itself, live, what information it needs and where to get it, and can take multiple steps if one search isn't enough. This is the foundational pattern behind real autonomous AI agents, not just a question-answering tool.

## How it works

1. **Thought** — the agent reasons about what it needs to find out
2. **Action** — it either searches the web with a specific query, or decides it has enough to answer
3. **Observation** — search results are fed back to the agent as new information
4. This loop repeats (up to 4 times) until the agent is confident, at which point it gives a final, grounded answer with sources

## Tech stack

- **Python**
- **Streamlit** — web interface
- **Google Gemini API** — reasoning and answer generation
- **ddgs (DuckDuckGo Search)** — free, no-key live web search tool

## Run it locally

1. Clone the repository and open the folder:

```
git clone https://github.com/alisha-tabassum/react-agent.git
cd react-agent
```

2. Install the dependencies:

```
pip install -r requirements.txt
```

3. Create a file named `.env` in the project folder and add your Gemini API key (free from Google AI Studio):

```
GEMINI_API_KEY=your_key_here
```

4. Start the app:

```
streamlit run app.py
```

## Project structure

```
react-agent/
├── app.py                  # Streamlit app: UI, ReAct reasoning loop, web search tool
├── requirements.txt        # Python dependencies
├── .streamlit/config.toml  # Streamlit theme configuration
└── .gitignore               # Keeps the API key out of GitHub
```

## Author

Alisha Tabassum, Computer Engineer
[LinkedIn](https://linkedin.com/in/alisha-tabassum)