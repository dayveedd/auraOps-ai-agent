import os
import json
from google import genai
from pydantic import BaseModel
from typing import Optional

# Configure Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "models/gemini-3-flash-preview"

class IntentData(BaseModel):
    action: str
    quantity: Optional[int] = None
    amount: Optional[int] = None
    currency: Optional[str] = None
    # Schedule event fields
    title: Optional[str] = None
    start_time: Optional[str] = None      # ISO 8601 format
    duration_minutes: Optional[int] = None
    description: Optional[str] = None
    attendees: Optional[list[str]] = None # List of attendee email addresses
    raw_response: str

def extract_intent(text: str) -> IntentData:
    """
    Parses a natural language instruction and returns the intended structured action.
    """
    prompt = f"""
    You are an AI assistant for AuraOps. You receive commands from users to perform actions.
    Extract the intent and parameters from the following text and return a strict JSON object.
    
    Valid actions: 
    - "provision_wallets" (requires 'quantity' and optionally 'amount' for starting balance)
    - "pay_vendor" (requires 'amount' and optionally 'currency')
    - "schedule_event" (requires 'title'; optionally 'start_time' in ISO 8601 format, 'duration_minutes', 'description', 'attendees')
    - "unknown" (if the intent is not clear)
    
    Text: "{text}"
    
    Output JSON format:
    {{
        "action": "provision_wallets" | "pay_vendor" | "schedule_event" | "unknown",
        "quantity": int | null,
        "amount": int | null,
        "currency": "NGN" | "USD" | null,
        "title": "event title string" | null,
        "start_time": "ISO 8601 datetime string e.g. 2025-04-01T14:00:00" | null,
        "duration_minutes": int | null,
        "description": "optional event description" | null,
        "attendees": ["email1@example.com", "email2@example.com"] | null
    }}
    
    Return ONLY valid JSON. Note that NGN amounts might be formatted like ₦10,000, which means amount = 10000.
    For schedule_event, infer start_time from phrases like "tomorrow at 2pm", "next Monday at 10am" etc.
    Current UTC time: {__import__('datetime').datetime.utcnow().isoformat()}
    """
    
    response = client.models.generate_content(model=MODEL, contents=prompt)
    
    try:
        # Strip markdown formatting if present
        result_text = response.text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        data = json.loads(result_text)
        return IntentData(
            action=data.get("action", "unknown"),
            quantity=data.get("quantity"),
            amount=data.get("amount"),
            currency=data.get("currency"),
            title=data.get("title"),
            start_time=data.get("start_time"),
            duration_minutes=data.get("duration_minutes"),
            description=data.get("description"),
            attendees=data.get("attendees"),
            raw_response=response.text
        )
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        return IntentData(action="unknown", raw_response=response.text)



