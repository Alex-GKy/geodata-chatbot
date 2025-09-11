"""Streamlit UI for the geodata chatbot."""

import streamlit as st

from src.agent.graph import graph

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page config
st.set_page_config(
    page_title="Geodata Chatbot",
    page_icon="🗺️",
    layout="centered"
)

# Header
st.title("🗺️ Geodata Chatbot")
st.markdown(
    "Chat with an AI assistant that specializes in geospatial data analysis.")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about geodata..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        try:
            # Create the input in the format expected by LangGraph
            input_data = {
                "messages": [{
                    "role": "human",
                    "content": prompt
                }]
            }

            # Call the graph directly - much simpler!
            result = graph.invoke(input_data)

            # Extract the assistant's response from the result
            if "messages" in result and result["messages"]:
                # Get the last message (should be from assistant)
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    full_response = last_message.content
                else:
                    full_response = str(last_message)
            else:
                full_response = "No response received"

            st.markdown(full_response)

        except Exception as e:
            full_response = f"Error: {str(e)}"
            st.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

# Sidebar with information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This chatbot is powered by LangGraph and specializes in geospatial data 
    analysis.
    
    **Features:**
    - Direct graph execution (no server needed)
    - Persistent chat history
    - Geospatial data expertise
    
    **Usage:**
    Just start chatting! The AI agent runs directly in the app.
    """)

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
