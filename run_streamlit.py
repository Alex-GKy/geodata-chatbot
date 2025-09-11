#!/usr/bin/env python3
"""Script to run the Streamlit geodata chatbot."""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app."""
    print("🗺️ Starting Geodata Chatbot Streamlit UI...")
    print("Access the app at: http://localhost:8501")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Add current directory to Python path
        env = os.environ.copy()
        env['PYTHONPATH'] = project_dir + ':' + env.get('PYTHONPATH', '')
        
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/streamlit_app.py",
            "--server.port", "8501"
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 Stopping Streamlit server...")
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())