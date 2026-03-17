import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from fastapi import APIRouter, Request
from auth0_ai_langchain.auth0_ai import Auth0AI

from services.gemini import extract_intent

auth0_ai = Auth0AI()
with_sign_in_with_slack_connection = auth0_ai.with_token_vault(
    connection="sign-in-with-slack",
    scopes=[
        "channels:read",
        "app_mentions:read",
        "chat:write"
    ]
)

app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN", "xoxb-dummy"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET", "dummy-secret")
)

handler = AsyncSlackRequestHandler(app)
router = APIRouter()

@router.post("/events")
async def endpoint(req: Request):
    return await handler.handle(req)

@app.event("app_mention")
async def handle_app_mentions(body, say):
    event = body.get("event", {})
    text = event.get("text", "")
    channel = event.get("channel", "")
    thread_ts = event.get("ts", "")
    
    intent = extract_intent(text)
    
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    
    if intent.action == "provision_wallets":
        quantity = intent.quantity or 50
        amount = intent.amount or 10000
        link = (
            f"{FRONTEND_URL}/authorize"
            f"?intent=provision_wallets"
            f"&channel={channel}"
            f"&thread_ts={thread_ts}"
            f"&quantity={quantity}"
            f"&amount={amount}"
        )
        await say(
            f"🤖 I need authorization to provision *{quantity}* wallets with a starting balance of *{amount}*."
            f" Please approve here: {link}",
            thread_ts=thread_ts
        )
    elif intent.action == "pay_vendor":
        amount = intent.amount or 500000
        link = (
            f"{FRONTEND_URL}/authorize"
            f"?intent=pay_vendor"
            f"&channel={channel}"
            f"&thread_ts={thread_ts}"
            f"&amount={amount}"
        )
        await say(
            f"🤖 I need authorization to pay a vendor *{amount}*."
            f" Please approve here: {link}",
            thread_ts=thread_ts
        )
    else:
        await say("I didn't quite get that. I can help provision wallets or pay vendors.", thread_ts=thread_ts)
