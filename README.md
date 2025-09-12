
Create or edit the .env file in the top folder with the OpenAI API key: 

```
OPENAI_API_KEY="sk-proj-..."
```

## Running the Application

### Option 1: Command Line Interface
```python
pip install -r requirements.txt
python src/client.py
```

### Option 2: Terminal UI (TUI)
```python
python src/tui_client.py
```

### Option 3: Streamlit Web UI
```python
# Install dependencies (if not already done)
uv pip install streamlit

# Run the Streamlit app
python run_streamlit.py
```

The Streamlit app will be available at http://localhost:8501

**Note:** Make sure the LangGraph server is running on localhost:2024 before using any of the clients.


