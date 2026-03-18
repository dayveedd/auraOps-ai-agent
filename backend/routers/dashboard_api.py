import os
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api", tags=["dashboard"])

class AgentAction(BaseModel):
    id: str
    type: str # 'wallet', 'payment', 'calendar'
    title: str
    status: str
    created_at: str
    link: Optional[str] = None
    amounts: Optional[str] = None

@router.get("/agent-actions", response_model=List[AgentAction])
async def get_agent_actions():
    """
    Fetches the unified action history from the Supabase databases: 
    wallets, transactions, and calendar_events.
    """
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if not url or not key:
            return []
            
        supabase = create_client(url, key)
        actions = []
        
        # 1. Fetch Wallets
        wallets_res = supabase.table("wallets").select("*").order("created_at", desc=True).limit(20).execute()
        for w in wallets_res.data:
            actions.append(AgentAction(
                id=w.get("id"),
                type="wallet",
                title="Provisioned Wallet",
                status=w.get("status", "active"),
                created_at=w.get("created_at"),
                amounts=f"Balance: ₦{int(w.get('balance', 0))}"
            ))
            
        # 2. Fetch Payments (Transactions)
        tx_res = supabase.table("transactions").select("*").order("created_at", desc=True).limit(20).execute()
        for t in tx_res.data:
            amount = int(t.get("amount", 0)) / 100 # Converting kobo to NGN
            actions.append(AgentAction(
                id=t.get("id"),
                type="payment",
                title=f"Paid Vendor ({t.get('reference')})",
                status=t.get("status", "unknown"),
                created_at=t.get("created_at"),
                link=t.get("paystack_url"),
                amounts=f"₦{amount:,.2f}"
            ))
            
        # 3. Fetch Calendar Events
        cal_res = supabase.table("calendar_events").select("*").order("created_at", desc=True).limit(20).execute()
        for c in cal_res.data:
            actions.append(AgentAction(
                id=c.get("id"),
                type="calendar",
                title=f"Scheduled: {c.get('title')}",
                status=c.get("status", "created"),
                created_at=c.get("created_at"),
                link=c.get("event_link")
            ))
            
        # Sort all actions by created_at descending
        actions.sort(key=lambda x: x.created_at, reverse=True)
        return actions[:50] # Return top 50 recent actions overall
        
    except Exception as e:
        print(f"Error fetching dashboard actions: {e}")
        return []
