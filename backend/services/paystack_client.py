import os
import time
import httpx
from typing import Dict, Any

PAYSTACK_BASE = "https://api.paystack.co"


def _paystack_headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ.get('PAYSTACK_SECRET_KEY', '')}",
        "Content-Type": "application/json"
    }


async def _record_transaction_in_supabase(transaction_data: dict) -> None:
    """Records a payment transaction in Supabase transactions table."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if url and key:
            supabase = create_client(url, key)
            supabase.table("transactions").insert(transaction_data).execute()
            print(f"Transaction recorded in Supabase: {transaction_data.get('reference', 'N/A')}")
    except Exception as e:
        print(f"Warning: Could not record transaction in Supabase: {e}")


async def pay_vendor(token: str, amount: int) -> Dict[str, Any]:
    """
    Records a vendor payment using Paystack's Initialize Transaction API.
    Creates a real transaction record on the Paystack test dashboard and
    also logs it to the Supabase transactions table simultaneously.
    Amount is in kobo (100 kobo = NGN 1).
    """
    secret_key = os.environ.get("PAYSTACK_SECRET_KEY", "")
    if not secret_key:
        return {"status": "error", "message": "Paystack credentials missing."}

    print(f"Initiating Paystack transaction for: NGN {amount / 100:.2f}")

    try:
        async with httpx.AsyncClient() as client:
            reference = f"AURAOPS-{int(time.time() * 1000)}"
            payload = {
                "email": "auraops-agent@auraops.io",
                "amount": amount,
                "currency": "NGN",
                "reference": reference,
                "metadata": {
                    "initiated_by": "AuraOps AI Agent",
                    "source": "slack_command"
                }
            }

            r = await client.post(
                f"{PAYSTACK_BASE}/transaction/initialize",
                json=payload,
                headers=_paystack_headers()
            )
            data = r.json()

            if data.get("status"):
                ref = data["data"]["reference"]
                payment_url = data["data"]["authorization_url"]

                # Log to Supabase transactions table
                await _record_transaction_in_supabase({
                    "reference": ref,
                    "amount": amount,
                    "currency": "NGN",
                    "status": "initialized",
                    "initiated_by": "AuraOps Agent",
                    "paystack_url": payment_url,
                })

                return {
                    "status": "success",
                    "message": (
                        f"Payment of NGN {amount / 100:.2f} initialized on Paystack. "
                        f"Reference: {ref}. Transaction recorded in database."
                    )
                }
            else:
                return {
                    "status": "error",
                    "message": f"Paystack error: {data.get('message')}"
                }

    except Exception as e:
        print(f"Paystack error: {e}")
        return {
            "status": "error",
            "message": f"Failed to process payment: {str(e)}"
        }



