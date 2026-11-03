import google.generativeai as genai
from dotenv import load_dotenv
import os
from ddgs import DDGS

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.5-flash-lite")

def search_web(query, max_results=3):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({"title": r["title"], "snippet": r["body"], "link": r["href"]})
    return results

SYSTEM_PROMPT = """You are a research agent that answers questions by searching the web.

You work in a loop of Thought, Action, Observation.

At each step, respond in EXACTLY this format (nothing else):

Thought: <your reasoning about what to do next>
Action: <either "search: <search query>" or "finish: <your final answer>">

Rules:
- Use "search: <query>" when you need more information.
- Use "finish: <answer>" only when you have enough information to answer confidently.
- Keep search queries short and specific.
- Do not make up information. Only answer using what you learned from search results.
- Give the final answer in 2-4 clear sentences.
"""

def run_agent(question, max_steps=4):
    history = f"Question: {question}\n"
    print(f"\n=== Question: {question} ===\n")

    for step in range(max_steps):
        prompt = SYSTEM_PROMPT + "\n" + history + "\nWhat is your next Thought and Action?"
        response = model.generate_content(prompt)
        text = response.text.strip()
        print(f"--- Step {step + 1} ---")
        print(text)
        print()

        history += text + "\n"

        if "Action: finish:" in text:
            final_answer = text.split("Action: finish:")[1].strip()
            print("=== FINAL ANSWER ===")
            print(final_answer)
            return final_answer

        if "Action: search:" in text:
            query = text.split("Action: search:")[1].strip()
            results = search_web(query)
            observation = "\n".join([f"- {r['title']}: {r['snippet'][:200]}" for r in results])
            print(f"[Searched: {query}]")
            print(f"Observation:\n{observation}\n")
            history += f"Observation: {observation}\n"

    print("Reached max steps without a final answer.")
    return None

if __name__ == "__main__":
    run_agent("What is the latest iPhone model released in 2026 and what is new about it?")


    