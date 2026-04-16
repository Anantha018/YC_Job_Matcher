# YC Job Matcher Agent
# github.com/Anantha018
# Licensed under MIT

import json
import time
from tqdm import tqdm
from colorama import Fore


def call_llm(prompt: str, provider: str, model: str, api_key: str = None, retries: int = 3) -> str:
    """
    Sends a prompt to the chosen LLM provider and returns the response.

    Supports 5 providers:
    - ollama  → free, runs locally, no API key needed
    - groq    → free tier, fast inference, needs GROQ API key
    - openai  → GPT models, needs OPENAI API key
    - claude  → Anthropic models, needs ANTHROPIC API key
    - gemini  → Google models, needs GEMINI API key

    Automatically retries on rate limit errors with exponential backoff:
    - Attempt 1 fail → wait 60s → retry
    - Attempt 2 fail → wait 120s → retry
    - Attempt 3 fail → wait 180s → skip batch

    Args:
        prompt:   The full prompt string to send to the LLM
        provider: One of "ollama", "groq", "openai", "claude", "gemini"
        model:    Model name string — if None uses provider default
        api_key:  API key for the provider — not needed for ollama
        retries:  Number of retry attempts on rate limit (default 3)

    Returns:
        Raw text response from the LLM as a string
    """
    for attempt in range(retries):
        try:
            if provider == "ollama":
                import ollama
                response = ollama.chat(
                    model=model or "llama3.1:8b",
                    messages=[{"role": "user", "content": prompt}],
                )
                return response["message"]["content"].strip()

            elif provider == "groq":
                from groq import Groq
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=model or "llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                return response.choices[0].message.content.strip()

            elif provider == "openai":
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model=model or "gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                return response.choices[0].message.content.strip()

            elif provider == "claude":
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model=model or "claude-haiku-4-5-20251001",
                    max_tokens=500,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text.strip()

            elif provider == "gemini":
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model or "gemini-2.5-flash",
                    contents=prompt
                )
                return response.text.strip()

            else:
                raise ValueError(f"Unknown provider: {provider}. Choose from: ollama, groq, openai, claude, gemini")

        except Exception as e:
            err = str(e).lower()
            if "rate" in err or "429" in err or "quota" in err:
                wait = 60 * (attempt + 1)
                tqdm.write(Fore.YELLOW + f"  Rate limit hit — waiting {wait}s before retry ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise e

    tqdm.write(Fore.RED + f"  Failed after {retries} retries — skipping batch")
    return "[]"


def extract_json(text: str) -> list:
    """
    Extracts a JSON array from raw LLM response text.

    LLMs sometimes wrap JSON in markdown code blocks or add
    extra text before/after. This function handles all cases:
    - Clean JSON response
    - JSON wrapped in ```json ... ``` blocks
    - JSON embedded somewhere in longer text

    Args:
        text: Raw string response from the LLM

    Returns:
        Parsed list from JSON, or empty list if parsing fails
    """
    text = text.strip()

    # try direct parse first
    try:
        return json.loads(text)
    except:
        pass

    # try stripping markdown code blocks
    if "```" in text:
        for block in text.split("```"):
            block = block.replace("json", "").strip()
            try:
                return json.loads(block)
            except:
                pass

    # try finding array by bracket position
    start = text.find("[")
    end = text.rfind("]") + 1
    if start != -1 and end > start:
        try:
            return json.loads(text[start:end])
        except:
            pass

    return []