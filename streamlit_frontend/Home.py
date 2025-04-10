import streamlit as st

st.set_page_config(
    page_title="RAG Chat Home",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Welcome to RAG Chat")

st.markdown("""
## Get Started

This application helps you interact with your documents using AI-powered chat. 

### Features:
- 💬 Chat with your documents
- 📚 Context-aware responses
- 🤖 Powered by Ollama LLM

### How to use:
1. Navigate to the "Chat" page using the sidebar
2. Ask questions about your documents
3. Get AI-generated responses based on document context

### Navigation:
- Use the sidebar to switch between pages
- Chat: Main chat interface
- About: Learn more about RAG technology
""")

with st.sidebar:
    st.success("Select a page above to get started!")
