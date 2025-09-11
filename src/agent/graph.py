"""LangGraph ReAct agent for geodata questions."""

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv(override=True)

# Initialize the LLM with streaming enabled
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

# llm = ChatOpenAI(
#     base_url="http://localhost:1234/v1",
#     streaming=True
# )

# Define tools (empty for now, we'll add geodata tools later)
tools = []

# Create the ReAct agent
graph = create_react_agent(llm, tools,
                           prompt="You are a helpful assistant, and an "
                                  "expert in geospatial data analysis.")
