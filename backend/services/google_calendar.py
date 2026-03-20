import os
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "..", "service_account.json")
SCOPES = ["https://www.googleapis.com/auth/calendar"]
# Calendar ID to write events to. Set GOOGLE_CALENDAR_ID to your own Google email
# so events appear in your calendar (requires sharing your calendar with the service account).
# If unset, events go to the service account's own calendar (not visible to you).
CALENDAR_ID = os.environ.get("GOOGLE_CALENDAR_ID", "primary")
# Email of the calendar owner - always added as attendee so events appear in their inbox
CALENDAR_OWNER_EMAIL = os.environ.get("GOOGLE_CALENDAR_OWNER_EMAIL", "")


def _get_calendar_service():
    """Returns an authenticated Google Calendar service client."""
    service_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    
    if service_json:
        # Load from environment variable (Production / Render)
        try:
            info = json.loads(service_json)
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )
        except json.JSONDecodeError:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON is not a valid JSON string.")
    else:
        # Fallback to local file (Local Development)
        if not os.path.exists(SERVICE_ACCOUNT_FILE):
             raise FileNotFoundError(
                 "No GOOGLE_SERVICE_ACCOUNT_JSON found in env, and local service_account.json is missing."
             )
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )
        
    return build("calendar", "v3", credentials=credentials)


async def _record_event_in_supabase(event_data: dict) -> None:
    """Records a calendar event in Supabase events table."""
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL", "")
        key = os.environ.get("SUPABASE_KEY", "")
        if url and key:
            supabase = create_client(url, key)
            supabase.table("calendar_events").insert(event_data).execute()
            print(f"Calendar event recorded in Supabase: {event_data.get('event_id', 'N/A')}")
    except Exception as e:
        print(f"Warning: Could not record event in Supabase: {e}")


async def schedule_event(
    token: str,
    title: str,
    start_time: Optional[str] = None,
    duration_minutes: int = 60,
    description: str = "",
    attendees: Optional[list] = None
) -> Dict[str, Any]:
    """
    Creates a Google Calendar event.
    - title: Event name/title
    - start_time: ISO format datetime string (e.g. '2024-03-20T14:00:00')
                  Defaults to 1 hour from now if not provided
    - duration_minutes: Duration in minutes (default 60)
    - description: Optional event description
    - attendees: Optional list of attendee email strings
    """
    try:
        service = _get_calendar_service()

        # Default start time to 1 hour from now if not provided
        if start_time:
            try:
                start_dt = datetime.fromisoformat(start_time)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=timezone.utc)
            except ValueError:
                start_dt = datetime.now(timezone.utc) + timedelta(hours=1)
        else:
            start_dt = datetime.now(timezone.utc) + timedelta(hours=1)

        end_dt = start_dt + timedelta(minutes=duration_minutes)

        actual_desc = description or "Event scheduled by AuraOps AI Agent"
        if attendees:
            actual_desc += "\n\nAttendees:\n" + "\n".join(f"- {a}" for a in attendees)

        event_body = {
            "summary": title,
            "description": actual_desc,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "UTC",
            },
        }

        # Note: service accounts cannot invite attendees on personal Gmail without
        # Domain-Wide Delegation (Google Workspace only). Events are written directly
        # to the shared calendar instead — they appear for the calendar owner automatically.

        print(f"Creating Google Calendar event: {title} at {start_dt.isoformat()}")

        event = service.events().insert(
            calendarId=CALENDAR_ID,
            body=event_body
        ).execute()

        event_id = event.get("id", "N/A")
        event_link = event.get("htmlLink", "")

        # Record in Supabase
        await _record_event_in_supabase({
            "event_id": event_id,
            "title": title,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_minutes": duration_minutes,
            "description": description,
            "event_link": event_link,
            "status": "created",
            "created_by": "AuraOps Agent",
        })

        return {
            "status": "success",
            "message": (
                f"📅 Event *{title}* scheduled for {start_dt.strftime('%b %d, %Y at %H:%M UTC')} "
                f"({duration_minutes} mins). "
                f"View: {event_link}"
            )
        }

    except Exception as e:
        print(f"Google Calendar error: {e}")
        return {
            "status": "error",
            "message": f"❌ Failed to schedule event: {str(e)}"
        }
