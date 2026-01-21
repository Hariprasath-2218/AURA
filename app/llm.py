import os
import requests
import json
import re

def generate_slides(topic):
    prompt = f"""
Generate exactly 8 PowerPoint slides about "{topic}"

RULES:
- Slide 1 is ONLY the title
- Slides 2–8 must each have:
  - A clear title
  - EXACTLY 3 bullet points
  - Each bullet point must be 1-2 full sentences long
- Output STRICT JSON only

FORMAT:
{{
  "slides": [
    {{
      "title": "Slide title",
      "bullets": ["point 1", "point 2", "point 3"]
    }}
  ]
}}
Respond ONLY with valid JSON. Do NOT include explanations, markdown, or code blocks.
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        },
        timeout=30
    )

    data = response.json()

    if "choices" not in data:
        raise RuntimeError(f"GROQ API ERROR: {data}")

    content = data["choices"][0]["message"]["content"]

    # Step 1: Strip code fences
    content = re.sub(r"^```(?:json)?\s*", "", content.strip())
    content = re.sub(r"\s*```$", "", content.strip())

    # Step 2: Try direct JSON parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Step 3: Try to extract and repair JSON manually
    try:
        json_match = re.search(r'\{[\s\S]*\}', content)
        if json_match:
            cleaned = json_match.group(0)

            # Fix common issues: add missing closing brackets for bullets
            cleaned = re.sub(r'"bullets":\s*\[[^\]]*?}(?=\s*,)', lambda m: m.group(0).replace('}', ']}'), cleaned)

            # Add missing commas between objects
            cleaned = re.sub(r'\}\s*\{', '}, {', cleaned)

            return json.loads(cleaned)
    except Exception as e:
        print("❌ JSON extraction failed:", e)

    # Final fallback: show error
    print("❌ JSON parsing failed completely.")
    print("🔎 Raw content returned:\n", content)
    raise RuntimeError("Failed to parse LLM response as JSON.")