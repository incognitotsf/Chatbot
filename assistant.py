import os
from datetime import date
from typing import Optional

from phi.agent import Agent
from phi.model.groq import Groq
from phi.tools.duckduckgo import DuckDuckGo


def create_agent(search: bool, api_key: Optional[str] = None) -> Agent:
    instructions = [
        f"Today's date is {date.today():%A, %d %B %Y}.",
        "Be clear and concise.",
    ]
    if search:
        instructions += [
            "For news, prices, releases or anything recent, search the web with DuckDuckGo first.",
            "After searching, answer from the results and list source links.",
        ]

    return Agent(
        model=Groq(
            id=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            api_key=api_key,
        ),
        tools=[DuckDuckGo()] if search else [],
        instructions=instructions,
        add_history_to_messages=True,
        num_history_responses=6,
        markdown=True,
    )
