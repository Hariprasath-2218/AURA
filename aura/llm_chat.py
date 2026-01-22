import os
import requests
from dotenv import load_dotenv
# from llama_cpp import Llama

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

SYSTEM_PROMPT = "You are AURA. Answer shortly and clearly in 2 lines."
MODEL_PATH = "models/qwen2.5-0.5b.Q4_K_M.gguf"


GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
LLAMACPP_URL = "http://localhost:8080/completion"


def ask_gemini(prompt):
    full_prompt = f"{SYSTEM_PROMPT}\n\nStudent: {prompt}"
    url = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"

    r = requests.post(
        url,
        json={"contents": [{"parts": [{"text": full_prompt}]}]},
        timeout=15
    )

    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]


def ask_groq(prompt):
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.5
        },
        timeout=20
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def ask_online_llm(prompt):
    try:
        return ask_gemini(prompt)
    except Exception as e:
        print("⚠️ Gemini failed:", e)
        return ask_groq(prompt)


def ask_llamacpp(prompt):
    system_prompt = (
        "You are AURA, a helpful robot assistant. "
        "Answer briefly and conversationally (2–3 lines max)."
    )

    payload = {
        "prompt": f"{system_prompt}\n\nStudent: {prompt}\nAURA:",
        "n_predict": 60,
        "temperature": 0.3,
        "stop": ["\nStudent:", "\nAURA:"]
    }

    try:
        r = requests.post(LLAMACPP_URL, json=payload, timeout=60)
        r.raise_for_status()
        return r.json().get("content", "").strip()
    except Exception as e:
        return f"Offline model error: {e}"

# llm = Llama(
#     model_path=MODEL_PATH,
#     n_ctx=2048,
#     n_threads=4,     # set to CPU cores of your Raspberry Pi
#     n_batch=256,
#     verbose=False
# )

# # =======================
# # LLaMA.cpp (Offline)
# # =======================

# def ask_llamacpp(prompt: str) -> str:
#     full_prompt = (
#         f"{SYSTEM_PROMPT}\n\n"
#         f"Student: {prompt}\n"
#         f"AURA:"
#     )

#     try:
#         output = llm(
#             full_prompt,
#             max_tokens=80,
#             temperature=0.3,
#             stop=["Student:", "AURA:"]
#         )

#         return output["choices"][0]["text"].strip()

#     except Exception as e:
#         return f"Offline model error: {e}"

