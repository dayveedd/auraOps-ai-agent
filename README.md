# 🌟 AuraOps AI Agent

AuraOps is a powerful, AI-driven operations agent designed to seamlessly orchestrate financial transactions, wallet provisioning, and calendar scheduling directly from Slack. Built with modern security and a microservices-like architecture, AuraOps acts as a bridge between human intention and complex API integrations.

## 🚀 Key Features

*   **🏦 Wallet Provisioning:** Automatically provision user wallets in Supabase with a specific starting balance.
*   **💸 Vendor Payments:** Initialize test-mode payments to vendors via the Paystack API and securely record transactions.
*   **📅 Google Calendar Scheduling:** Use natural language to schedule meetings, complete with dynamic attendee extraction, pushing events directly to Google Calendar.
*   **🔐 Auth0 Token Vault Integration:** Ensures that every sensitive action requested via Slack is securely authenticated and authorized via a modern glassmorphic web dashboard before execution.
*   **🧠 Gemini AI Powered:** Utilizes Google's Gemini Flash model to parse and extract structured intent (`action`, `amount`, `quantity`, `attendees`, etc.) from natural language Slack messages.
*   **📊 Unified Action History:** A sleek React dashboard that pulls real-time, unified agent logs across Wallets, Payments, and Calendar events directly from Supabase.

## 🛠️ Technology Stack

**Frontend:**
*   React 18 + Vite
*   TypeScript
*   Tailwind CSS (with Glassmorphism aesthetics)
*   Auth0 React SDK (`@auth0/auth0-react`)
*   Lucide React (Icons)

**Backend:**
*   Python 3 + FastAPI
*   Uvicorn (ASGI server)
*   Slack Bolt (`slack_bolt`)
*   Google GenAI (`google-genai`)
*   Auth0 AI Langchain Token Vault
*   Supabase Python Client
*   Google API Python Client (Calendar v3)
*   Paystack API (via `httpx`)

## 🏗️ Architecture Flow

1.  **User Request:** A user mentions the bot in Slack (e.g., *"@AuraOps schedule a sync with client@example.com tomorrow at 3pm for 30 minutes"*).
2.  **Intent Extraction:** The Slack Bolt app routes the message to the Gemini AI model, which parses the natural language into structured JSON data.
3.  **Authorization:** The bot replies in Slack with a secure Auth0 authorization link, carrying the extracted parameters in the URL.
4.  **Verification:** The user clicks the link, lands on the React Dashboard, logs in via Auth0, and reviews the exact action the agent intends to take on their behalf.
5.  **Execution:** Upon clicking *Authorize*, the frontend sends a POST callback to the backend FastAPI server, which executes the requested tool (Supabase, Paystack, or Google Calendar).
6.  **Confirmation:** The backend returns success, the frontend updates to the success state, and the Slack bot replies in the original thread confirming the action is complete.

## 💾 Project Structure

```
AuraOps/
├── backend/
│   ├── main.py                 # FastAPI application and routers registration
│   ├── routers/
│   │   ├── auth.py             # Auth0 callback execution endpoints
│   │   ├── dashboard_api.py    # Unified Action History API endpoint
│   │   └── slack.py            # Slack event listeners and Bot routing
│   └── services/
│       ├── gemini.py           # Gemini inference and intent extraction
│       ├── google_calendar.py  # Google Calendar service account integration
│       ├── paystack_client.py  # Paystack transaction API
│       └── supabase_client.py  # Supabase lazy initialization and queries
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── ActionHistory.tsx # Unified agent log timeline
    │   │   ├── Dashboard.tsx     # Authorization view and Command Center
    │   │   └── Login.tsx         # Auth0 login entrypoint
    │   ├── App.tsx             # React Router and Auth0 state protection
    │   └── index.css           # Tailwind configuration and abstract backgrounds
```

## ⚙️ Environment Configuration

To run this project, you need `.env` files in both the `backend` and `frontend` directories.

### Backend (`backend/.env`)
Required variables (see `backend/.env.example`):
*   `SLACK_BOT_TOKEN`, `SLACK_SIGNING_SECRET`, `SLACK_APP_TOKEN`
*   `GEMINI_API_KEY`
*   `AUTH0_DOMAIN`, `AUTH0_CLIENT_ID`, `AUTH0_AUDIENCE`
*   `SUPABASE_URL`, `SUPABASE_KEY` (Requires Service Role key to bypass RLS)
*   `PAYSTACK_SECRET_KEY`
*   `GOOGLE_CALENDAR_ID`, `GOOGLE_CALENDAR_OWNER_EMAIL` (For proper calendar visibility)

*(Note: You must also place your `service_account.json` downloaded from Google Cloud in the `backend/` root).*

### Frontend (`frontend/.env`)
Required variables (see `frontend/.env.example`):
*   `VITE_AUTH0_DOMAIN`, `VITE_AUTH0_CLIENT_ID`, `VITE_AUTH0_AUDIENCE`
*   `VITE_BACKEND_URL` (Usually `http://localhost:8000` or an ngrok tunnel)

## 💻 Running the Application

### 1. Start the Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt # (ensure all dependencies are installed)
uvicorn main:app --reload --port 8000
```
*If using Slack Events API locally, expose port 8000 using ngrok:*
```bash
ngrok http 8000
```

### 2. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```

## 🛑 Agent Capabilities & Commands

The Agent is heavily prompted to safely and strictly adhere to explicit commands:

*   **"provision 50 wallets with a starting balance of 10000"** -> Extracts quantity (50) and amount (10000), calls Supabase.
*   **"pay a vendor 5000"** -> Extracts amount (5000), calls Paystack Initialize Transaction API.
*   **"schedule a vendor review with john@example.com tomorrow at 2pm for 45 minutes"** -> Extracts title, start_time (ISO8601), duration_minutes, and attendees array. Calls Google Calendar API.

Any ambiguous or wildly different requests are intentionally blocked by the Gemini model setup returning an `unknown` intent, which the Slackbot handles gracefully with a help menu.
