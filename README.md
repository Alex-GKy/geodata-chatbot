Create or edit the .env file in the top folder with the OpenAI API key:

```
OPENAI_API_KEY="sk-proj-..."
```

## Running the Application

### Option 1: Command Line Interface

```shell
pip install - r requirements.txt
python src / client.py
```

### Option 2: Terminal UI (TUI)

```shell
python src / tui_client.py
```

### Option 3: Streamlit Web UI

```shell
# Install dependencies (if not already done)
uv pip install streamlit

# Run the Streamlit app
python run_streamlit.py
```

## Streamlit Deployment

### Secrets file
When deployed to streamlit.io, the app will use
secrets (https://docs.streamlit.io/develop/concepts/connections/secrets-management)
These can be used locally as well and have to be put into .streamlit/secrets.toml

The Streamlit app will be available at http://localhost:8501

### Config file

You need a .streamlit/config.toml file that contains setup for running locally:

```toml
[server]
headless = true

[global]
# Specify the path to the main application file
mainScript = "src/streamlit_app.py"
```

### Password setting

In the secrets.toml, set a password like so: 

```toml
PASSWORD="pass"
DEBUG="true"
```

If the ```DEBUG``` flag is set to ```True```, the password check will be skipped


