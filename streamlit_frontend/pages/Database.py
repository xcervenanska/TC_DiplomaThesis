import streamlit as st
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path='../../.env')
BACKEND_URL = os.getenv('BACKEND_URL')

def make_request(endpoint: str, method: str = "GET", json_data: dict = None, files: list = None):
    try:
        url = f"{BACKEND_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif files:
            response = requests.post(url, files=files)
        else:
            response = requests.post(url, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None

def get_config():
    return make_request("config")

st.title("Document Database Management")

# File upload section
st.header("Upload Documents")
uploaded_files = st.file_uploader("Choose PDF files", type=['pdf'], accept_multiple_files=True)

if uploaded_files:
    if st.button("Process and Ingest Files"):
        files = [("files", file) for file in uploaded_files]
        response = make_request("documents/upload", method="POST", files=files)
        
        if not response:
            st.error("Failed to upload documents")
        elif response.get("status") == "success":
            st.success(response.get("message", "Successfully uploaded files!"))
        else:
            st.error("Failed to upload documents: " + response.get("message", "Unknown error"))

# Document listing section
st.header("Stored Documents")
if st.button("List Documents"):
    results = make_request("documents")
    if results and results.get('documents'):
        df_data = {
            'Source': [m.get('source', 'Unknown') for m in results['metadatas']],
            'Content': results['documents']
        }
        
        st.dataframe(
            df_data,
            column_config={
                'Source': st.column_config.TextColumn('Source File'),
                'Content': st.column_config.TextColumn('Content', width='large')
            },
            hide_index=True
        )
        
        st.info(f"Total chunks: {len(results['documents'])}")
    else:
        st.info("No documents found in the database.")

# Add clear database option
if st.button("Clear Database"):
    response = make_request("documents/clear", method="POST")
    if response and response["status"] == "success":
        st.success("Database cleared successfully!")
    else:
        st.error("Failed to clear database")
