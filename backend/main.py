import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from auth0_ai_langchain.auth0_ai import Auth0AI

# Load env variables before importing routers
load_dotenv(override=True)

from routers import slack, auth, dashboard_api

app = FastAPI(title="AuraOps API")

frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")

# Add CORS middleware to allow the Vite frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://auraops-ai.vercel.app",
        frontend_url
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(slack.router, prefix="/slack")
app.include_router(auth.router)
app.include_router(dashboard_api.router)

@app.get("/")
def read_root():
    return {"message": "AuraOps Backend is running"}
