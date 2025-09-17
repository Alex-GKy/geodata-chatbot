"""LangGraph ReAct agent for geodata questions."""

import os
import shutil
import tempfile

import streamlit as st
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from utils.config import is_mining_case_enabled
from .mining_tools import MINING_TOOLS

# Load secrets from Streamlit (works for both local .streamlit/secrets.toml
# and cloud)
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
    files_to_copy = []

    # Add dataset-specific files based on mining case setting
    if is_mining_case_enabled():
        files_to_copy.append("3D_point_cloud_GT-100k.csv")
    else:
        files_to_copy.extend([
            "demo_scene_c.usda",
            "indoor_room_labelled_sparse.csv"
        ])

    if os.path.exists(DATA_DIR):
        for file in files_to_copy:
            source_path = os.path.join(DATA_DIR, file)
            if os.path.exists(source_path):
                dest_path = os.path.join(TEMP_WORKSPACE, file)
                shutil.copy2(source_path, dest_path)
    print(TEMP_WORKSPACE)


setup_workspace()

# Initialize the LLM with streaming enabled
llm = ChatOpenAI(model="gpt-4o", temperature=0, streaming=True)

# llm = ChatOpenAI(
#     base_url="http://localhost:1234/v1",
#     streaming=True
# )


# Create file management toolkit for the temporary workspace
file_toolkit = FileManagementToolkit(
    root_dir=TEMP_WORKSPACE,
    selected_tools=["read_file", "list_directory", "file_search"]
)


# Define tools based on mode
tools = file_toolkit.get_tools()

if is_mining_case_enabled():
    # Add mining-specific tools
    tools.extend(MINING_TOOLS)

# Create the ReAct agent with mode-specific prompt
if is_mining_case_enabled():
    prompt = ("You are a helpful assistant and expert in "
              "geospatial data analysis, specifically mining operations. "
              "You have access to a mining point cloud dataset."
              "Use 'list_directory' to see available files, but never attempt"
              "to open a csv file."
              "You have multiple tools available to answer questions. If "
              "asked for information about this mine, try to answer the "
              "question using your tools. If you don't have relevant tools "
              "available, tell the user so."
              "Use these tools whenever required, but never attempt to read"
              "the csv file yourself"
              "If you can, avoid telling the user that you can't read the csv"
              "file - only tell them if they specifically ask for it")
else:
    prompt = ("You are a helpful assistant and expert in "
              "geospatial data analysis. "
              "All USD files are already available in "
              "the workspace. "
              "Use 'list_directory' to see available "
              "files and 'read_file' "
              "to analyze USD scene content when needed."
              "Make sure to strictly only read USD* files")

graph = create_react_agent(llm, tools, prompt=prompt)
