import json
import requests
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
import os

# Load environment variables
root_dir = Path(__file__).parent.parent.parent
load_dotenv(dotenv_path=root_dir / '.env', override=True)
BACKEND_URL = f"{os.getenv('BACKEND_URL')}/query"
MODEL = os.getenv('OLLAMA_MODEL')

def test_backend_connection() -> bool:
    try:
        with requests.post(
            BACKEND_URL,
            json={"question": "test", "messages": []},
            stream=True,
            headers={"Accept": "text/event-stream"}
        ) as response:
            response.raise_for_status()
            return next(response.iter_lines(), None) is not None
    except requests.exceptions.RequestException:
        return False

# Page setup
st.set_page_config(page_title="RAG Chat", page_icon="💬", layout="wide")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "backend_connected" not in st.session_state:
    st.session_state.backend_connected = test_backend_connection()

# Welcome message
if not st.session_state.messages:
    st.markdown("""
    👋 **Welcome to RAG Chat!**
    Ask any question about the documents in our database.
    """)

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat interface
if st.session_state.backend_connected:
    if prompt := st.chat_input("What would you like to know?", max_chars=500):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                with requests.post(
                    BACKEND_URL,
                    json={"question": prompt, "messages": st.session_state.messages[:-1]},
                    stream=True,
                    headers={"Accept": "text/event-stream"}
                ) as response:
                    response.raise_for_status()
                    
                    for line in response.iter_lines():
                        if line and (line := line.decode('utf-8')).startswith('data: '):
                            try:
                                content = json.loads(line[6:]).get('answer', '')
                                full_response += content
                                message_placeholder.markdown(full_response + "▌")
                            except json.JSONDecodeError:
                                continue
                    
                    if not full_response.strip():
                        full_response = "I apologize, but I couldn't generate a response."
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})

            except requests.exceptions.RequestException as e:
                st.error(f"Error: {str(e)}")
else:
    st.error("Unable to connect to the backend service.")
    if st.button("Retry Connection"):
        st.session_state.backend_connected = test_backend_connection()
        st.rerun()

# Sidebar
with st.sidebar:
    st.header("Chat Controls")
    
    # Connection status
    status = "🟢 Connected" if st.session_state.backend_connected else "🔴 Disconnected"
    st.markdown(f"**Status:** {status}")
    
    # Model info
    st.markdown("---")
    st.markdown(f"**Model:** {MODEL}")
    
    # Clear chat button
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
