import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.services.llm_helper import llm_helper

test_prompts = [
    "Can you find some lead for me?",
    "You can find lead which have missing website in Mohammedpur region.",
    "You can find lead for me which have missing website in Dhaka of Gymnastics.",
    "do it foe me",
    "Can you find leads ? The lead have whatsapp number",
    "How should I price a $1,500/month retainer?",
    "Write a cold email for Toit Brewpub"
]

def parse_intent(msg: str, default_loc="Dhaka", default_cat="Gym"):
    prompt = f"""You are an AI Agent Router for a lead generation and agency sales platform.
Analyze the user's message and determine whether they are requesting the AI to FIND/SCOUT leads or businesses, or if they are asking a general conversational/strategy question.

User Message: "{msg}"
Default Context Location: "{default_loc}"
Default Context Category: "{default_cat}"

Return ONLY a JSON object with keys:
- "action": "FIND_LEADS" | "AUDIT" | "CHAT"
- "category": extracted business category (or default if implied)
- "area": extracted area/neighborhood (or empty if not mentioned)
- "city": extracted city (or default if implied)
- "require_missing_website": boolean (true if user wants leads without website or missing website)
- "require_whatsapp": boolean (true if user specifically wants WhatsApp/phone)

JSON:"""

    resp = llm_helper.call_llm([{"role": "user", "content": prompt}], temperature=0.0)
    clean = resp.strip()
    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(clean.strip())

for p in test_prompts:
    res = parse_intent(p, "Dhaka", "Gym")
    print(f"Prompt: '{p}' -> Action: {res.get('action')}, Cat: {res.get('category')}, Area: {res.get('area')}, City: {res.get('city')}, NoWeb: {res.get('require_missing_website')}, WA: {res.get('require_whatsapp')}")
