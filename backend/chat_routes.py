import re
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agent import run_agent


router = APIRouter(
    prefix="/api",
    tags=["Chat & Intelligence"]
)


class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    answer: str
    suggestions: List[str]


def format_agent_response(raw_output: str) -> dict:
    """
    Separates the agent's main answer from
    its suggested follow-up questions.
    """

    marker = re.search(
        r"(?im)^[ \t]*(?:#{1,6}[ \t]*)?(?:\*\*|__)?"
        r"S?uggested Follow[-\u2010-\u2015]up Questions(?::)?(?:\*\*|__)?"
        r"[ \t]*:?[ \t]*(?:\r?\n|$)",
        raw_output,
    )

    if marker:
        answer_part = raw_output[:marker.start()]
        suggestions_part = raw_output[marker.end():]
        suggestions = []
        for line in suggestions_part.splitlines():
            suggestion = re.sub(r"^[ \t]*(?:[-*+]|\d+[.)])[ \t]*", "", line)
            suggestion = suggestion.strip().strip("*_` ")
            if suggestion:
                suggestions.append(suggestion)
    else:
        answer_part = raw_output
        suggestions = []

    return {
        "answer": answer_part.strip(),
        "suggestions": suggestions
    }


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat_endpoint(req: ChatRequest):

    if not req.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    try:
        raw_output = run_agent(req.query)

        return format_agent_response(raw_output)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )