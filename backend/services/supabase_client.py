import os
from typing import Dict, Any
from supabase import create_client, Client

def _get_client() -> Client | None:
    """Returns a fresh Supabase client using current env vars."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_KEY", "")
    if url and key:
        return create_client(url, key)
    return None

async def provision_wallets(token: str, quantity: int, amount: int) -> Dict[str, Any]:
    """
    Provisions wallets in Supabase.
    """
    supabase = _get_client()
    if not supabase:
        return {"status": "error", "message": "Supabase credentials missing."}

    print(f"Provisioning {quantity} wallets in Supabase with starting balance of {amount}.")
    print(f"Using Supabase URL: {os.environ.get('SUPABASE_URL', 'NOT SET')}")
    print(f"Key prefix: {os.environ.get('SUPABASE_KEY', '')[:20]}...")

    try:
        wallets_to_insert = [{"balance": amount, "status": "active"} for _ in range(quantity)]
        response = supabase.table("wallets").insert(wallets_to_insert).execute()

        return {
            "status": "success",
            "message": f"✅ {len(response.data)} wallets successfully provisioned with starting balance of {amount}."
        }
    except Exception as e:
        print(f"Supabase error: {e}")
        return {
            "status": "error",
            "message": f"❌ Failed to provision wallets: {str(e)}"
        }
