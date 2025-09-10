"""LangGraph chat agent for geodata questions."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from langgraph.graph import StateGraph
from langgraph.runtime import Runtime


class Context(TypedDict):
    """Context parameters for the agent."""
    my_configurable_param: str


class State(TypedDict):
    """State for the chat agent."""
    messages: List[BaseMessage]


async def chat_node(state: State, runtime: Runtime[Context]) -> Dict[str, Any]:
    """Process messages and return a response."""
    messages = state.get("messages", [])
    
    if not messages:
        return {"messages": [AIMessage(content="Hello! How can I help you with geodata questions?")]}
    
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        # Simple echo response for now
        response = AIMessage(content=f"You asked: {last_message.content}")
        return {"messages": messages + [response]}
    
    return {"messages": messages}


# Define the graph
graph = (
    StateGraph(State, context_schema=Context)
    .add_node("chat", chat_node)
    .add_edge("__start__", "chat")
    .compile(name="Geodata Chat Agent")
)
