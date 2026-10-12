import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
agents: dict[bool, Agent] = {}
INDEX_FILE = Path(__file__).resolve().parent / "index.html"


class ChatIn(BaseModel):
    message: str
    search: bool = True


def get_agent(search: bool) -> Agent:
    key = search
    if key not in agents:
        instructions = [
            f"Today's date is {date.today():%A, %d %B %Y}.",
            "Be clear and concise.",
        ]
        if search:
            instructions += [
                "For news, prices, releases or anything recent, search the web with DuckDuckGo first.",
                "After searching, answer from the results and list source links.",
            ]
        agents[key] = Agent(
            model=Groq(id=GROQ_MODEL),
            tools=[DuckDuckGo()] if search else [],
            instructions=instructions,
            add_history_to_messages=True,
            num_history_responses=6,
            markdown=True,
        )
    return agents[key]


@app.post("/api/chat")
def chat(body: ChatIn):
    def stream():
        if not os.getenv("GROQ_API_KEY"):
            yield "Groq key missing. Add GROQ_API_KEY to your .env file and restart."
            return
        try:
            agent = get_agent(body.search)
            for chunk in agent.run(body.message, stream=True):
                if chunk.content:
                    yield str(chunk.content)
        except Exception as e:
            yield f"\n\nError: {e}."

    return StreamingResponse(stream(), media_type="text/plain; charset=utf-8")


@app.post("/api/reset")
def reset():
    agents.clear()
    return {"ok": True}


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/")
def index():
    return FileResponse(INDEX_FILE)
