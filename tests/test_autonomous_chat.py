import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.stdout.reconfigure(encoding='utf-8')

from src.services.agent_chat import agent_chat_service

user_prompt = "You can find lead for me which have missing website in Dhaka of Gymnastics."
print(f"=== TESTING USER PROMPT: '{user_prompt}' ===")
response = agent_chat_service.respond(
    agent_name="Apex",
    user_message=user_prompt,
    current_leads=[],
    agency_goal="Website Development",
    location_str="Dhaka, Bangladesh"
)
print("=== RESPONSE ===")
print(response)
print("Discovered leads count in service:", len(agent_chat_service.last_discovered_leads))
