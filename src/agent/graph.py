"""LangGraph ReAct agent for geodata questions."""

import os
import shutil
import tempfile

import streamlit as st
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

# Load secrets from Streamlit (works for both local .streamlit/secrets.toml and cloud)
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
if "LANGCHAIN_API_KEY" in st.secrets:
    os.environ["LANGCHAIN_API_KEY"] = st.secrets["LANGCHAIN_API_KEY"]


# Create temporary workspace for file operations
TEMP_WORKSPACE = tempfile.mkdtemp(prefix="geodata_workspace_")
DATA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "DATA")


# Copy specific files to workspace at startup
def setup_workspace():
    """Copy specific files from DATA directory to temporary workspace."""
    # Hard-coded list of files to copy
    files_to_copy = [
        "demo_scene_c.usda",
        "indoor_room_labelled_sparse.csv",
        # Add more files here as needed
    ]

    if os.path.exists(DATA_DIR):
        for file in files_to_copy:
            source_path = os.path.join(DATA_DIR, file)
            if os.path.exists(source_path):
                dest_path = os.path.join(TEMP_WORKSPACE, file)
                shutil.copy2(source_path, dest_path)


setup_workspace()

# Initialize the LLM with streaming enabled
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, streaming=True)

# llm = ChatOpenAI(
#     base_url="http://localhost:1234/v1",
#     streaming=True
# )


# Create file management toolkit for the temporary workspace
file_toolkit = FileManagementToolkit(
    root_dir=TEMP_WORKSPACE,
    selected_tools=["read_file", "list_directory", "file_search"]
)

# Define tools
tools = file_toolkit.get_tools()

# Create the ReAct agent
graph = create_react_agent(llm, tools,
                           prompt="You are a helpful assistant and expert in "
                                  "geospatial data analysis. "
                                  "All USD files are already available in "
                                  "the workspace. "
                                  "Use 'list_directory' to see available "
                                  "files and 'read_file' "
                                  "to analyze USD scene content when needed."
                                  "Make sure to strictly only read USD* files")
