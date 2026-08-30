# ============================================================
# CITY INTELLIGENCE FASTAPI BACKEND
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent import run_agent


# ============================================================
# CREATE APPLICATION
# ============================================================

app = FastAPI(
    title="City Intelligence API",
    description="AI-powered City Intelligence Assistant",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    message: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "City Intelligence API is running."
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "status": "healthy"
    }


# ============================================================
# ASK AGENT
# ============================================================

@app.post("/ask")
def ask_agent(request: ChatRequest):

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if not request.message.strip():

        return {
            "success": False,
            "answer": "Please enter a message."
        }


    # --------------------------------------------------------
    # Run agent
    # --------------------------------------------------------

    try:

        answer = run_agent(
            request.message
        )


        return {
            "success": True,
            "answer": answer
        }


    except Exception as e:

        print(
            "Agent Error:",
            e
        )


        return {
            "success": False,
            "answer": (
                "⚠️ Something went wrong.\n\n"
                "Please try again."
            )
        }