"""Streamlit UI for the geodata chatbot."""

import streamlit as st

from agent.graph import graph
from components.point_cloud_viewer import show_point_cloud_viewer

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Page config
st.set_page_config(
    page_title="Geodata Chatbot",
    page_icon="🌍",
    layout="wide"
)


# Load and apply custom CSS
def load_css():
    try:
        with open("styles.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # CSS file not found, continue without custom styling
        pass


load_css()

# Header with enhanced styling
st.markdown('<h1 class="main-header">🌍 Geodata Intelligence Hub 🛰️</h1>',
            unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">🗺️ Your AI-powered geospatial data analysis '
    'companion 📊</p>',
    unsafe_allow_html=True)

# Add some visual flair with columns and metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🌐 Global Coverage</h3>
        <p>Worldwide geospatial data</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>⚡ Real-time Analysis</h3>
        <p>Instant data processing</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>🎯 Precise Results</h3>
        <p>Accurate geospatial insights</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input with enhanced placeholder
if prompt := st.chat_input(
        "🌍 Ask me about satellite data, GIS analysis, mapping, coordinates, "
        "or any geodata topic..."):
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

            # Show enhanced thinking indicator
            message_placeholder.markdown("🛰️ *Analyzing ...*")

            # Use LangGraph's token-level streaming
            full_response = ""
            for chunk in graph.stream(input_data, stream_mode="messages"):
                # Check if chunk is an AIMessageChunk and get content
                if chunk[0].type == "AIMessageChunk" and chunk[0].content:
                    # Ensure proper spacing between chunks
                    chunk_content = chunk[0].content
                    if full_response and not full_response.endswith(
                            ' ') and not chunk_content.startswith(' '):
                        # Add space if needed between chunks
                        if not full_response.endswith(
                                ('.', '!', '?', ':', '\n')):
                            chunk_content = ' ' + chunk_content

                    full_response += chunk_content
                    message_placeholder.markdown(full_response + "📍")

            # Remove cursor and show final response
            if full_response:
                message_placeholder.markdown(full_response)
            else:
                full_response = "🔍 No geospatial data found for your query"
                message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = f"⚠️ Geospatial analysis error: {str(e)}"
            message_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response})

# Enhanced sidebar with geodata theme
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

    # Point Cloud Viewer - always visible
    st.markdown("### 🌐 3D Visualization")
    show_point_cloud_viewer()

    st.markdown("---")

    st.markdown("## 🌍 Geodata Intelligence")

    st.markdown("""
    <div class="feature-box">
        <h4>🛰️ Satellite Data Analysis</h4>
        <p>Process and analyze satellite imagery and remote sensing data</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
        <h4>🗺️ GIS Operations</h4>
        <p>Perform spatial analysis, mapping, and geographic calculations</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-box">
        <h4>📊 Spatial Statistics</h4>
        <p>Generate insights from geospatial datasets and coordinates</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### 🔧 Tools & Features")
    st.markdown("""
    - 🌐 **Global Coordinate Systems**
    - 📐 **Spatial Measurements**
    - 🗂️ **Data Format Conversion**
    - 📈 **Visualization Support**
    - 🔍 **Location Intelligence**
    """)

    st.markdown("---")

    # Enhanced clear button
    if st.button("🗑️ Clear Chat History", help="Clear all messages"):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown("### 📍 Quick Tips")
    st.info("""
    💡 **Try asking about:**
    - Coordinate conversions
    - Satellite imagery analysis
    - GIS data processing
    - Spatial relationships
    - Map projections
    - Geographic calculations
    """)

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer-text">
    🌍 Powered by AI • Built for Geospatial Excellence • 🛰️
</div>
""", unsafe_allow_html=True)
