from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from services.supabase_client import provision_wallets
from services.paystack_client import pay_vendor
from routers.slack import app as slack_app

router = APIRouter(prefix="/auth", tags=["auth"])

class AuthCallback(BaseModel):
    token: str
    intent: str
    channel: Optional[str] = None
    thread_ts: Optional[str] = None
    quantity: Optional[int] = 50
    amount: Optional[int] = 10000

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
