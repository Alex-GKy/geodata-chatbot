"""LangGraph ReAct agent for geodata questions."""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Define tools (empty for now, we'll add geodata tools later)
tools = []

# Create the ReAct agent
graph = create_react_agent(llm, tools,
                           prompt="You are a helpful assistant, and an "
                                  "expert in geospatial data analysis.")
