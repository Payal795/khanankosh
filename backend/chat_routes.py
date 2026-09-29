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

    marker = "Suggested Follow-up Questions:"

    if marker in raw_output:
        answer_part, suggestions_part = raw_output.split(
            marker,
            1
        )

        suggestions = [
            line.strip(" 0123456789.-*")
            for line in suggestions_part.strip().split("\n")
            if line.strip()
        ]
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