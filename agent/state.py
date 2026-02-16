"""
LangGraph State Definition
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    State object for the agent graph
    """
    # Conversation messages
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # User query
    query: str

    # Query classification
    query_type: str
    query_boost_keywords: str

    # Retrieved context from documents
    context: str
    retrieved_sections: list

    # Decision from router
    next_action: str

    # Tool calls and results
    tool_calls: list
    tool_results: list

    # Final response
    response: str

    # Iteration counter
    iteration: int

