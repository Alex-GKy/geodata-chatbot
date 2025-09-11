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
        message_placeholder = st.empty()
        
        try:
            # Create the input in the format expected by LangGraph
            input_data = {
                "messages": [{
                    "role": "human",
                    "content": prompt
                }]
            }
            
            # Show initial thinking indicator
            message_placeholder.markdown("🤖 *Thinking...*")
            
            # Use LangGraph's token-level streaming
            full_response = ""
            for chunk in graph.stream(input_data, stream_mode="messages"):
                # Check if chunk is an AIMessageChunk and get content
                if chunk[0].type == "AIMessageChunk" and chunk[0].content:
                    full_response += chunk[0].content
                    message_placeholder.markdown(full_response + "▌")

            # Remove cursor and show final response
            if full_response:
                message_placeholder.markdown(full_response)
            else:
                full_response = "No response received"
                message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"Error: {str(e)}"
            message_placeholder.markdown(full_response)

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
    - Real-time streaming responses
    - Direct graph execution (no server needed)
    - Persistent chat history
    - Geospatial data expertise
    
    **Usage:**
    Just start chatting! The AI agent runs directly in the app.
    """)

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
