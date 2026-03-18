from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from services.supabase_client import provision_wallets
from services.paystack_client import pay_vendor
from services.google_calendar import schedule_event
from routers.slack import app as slack_app

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthCallback(BaseModel):
    token: str
    intent: str
    channel: Optional[str] = None
    thread_ts: Optional[str] = None
    quantity: Optional[int] = 50
    amount: Optional[int] = 10000
    # Calendar event fields
    title: Optional[str] = None
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = 60
    description: Optional[str] = None
    attendees: Optional[str] = None

@router.post("/callback")
async def handle_auth_callback(callback: AuthCallback):
    try:
        response_msg = ""
        if callback.intent == "provision_wallets":
            result = await provision_wallets(callback.token, callback.quantity or 50, callback.amount or 10000)
            response_msg = result["message"]
        elif callback.intent == "pay_vendor":
            result = await pay_vendor(callback.token, callback.amount or 500000)
            response_msg = result["message"]
        elif callback.intent == "schedule_event":
            attendees_list = [email.strip() for email in callback.attendees.split(",")] if callback.attendees else None
            result = await schedule_event(
                token=callback.token,
                title=callback.title or "AuraOps Meeting",
                start_time=callback.start_time,
                duration_minutes=callback.duration_minutes or 60,
                description=callback.description or "",
                attendees=attendees_list
            )
            response_msg = result["message"]
        else:
            response_msg = "❌ Unknown intent authorized."

        # Send completion message back to original Slack thread
        if callback.channel:
            await slack_app.client.chat_postMessage(
                channel=callback.channel,
                thread_ts=callback.thread_ts,
                text=response_msg
            )
            
        return {"status": "success", "message": "Authorized and executed"}
    except Exception as e:
        print(f"Error handling callback: {e}")
        return {"status": "error", "message": str(e)}
