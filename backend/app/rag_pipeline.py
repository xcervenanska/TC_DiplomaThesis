import os
from typing import AsyncGenerator, List
from app.ollama_integration import OllamaAPI
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (where .env is located)
root_dir = Path(__file__).resolve().parents[2]  # Go up 2 levels from rag_pipeline.py
env_path = root_dir / '.env'

# Load the environment variables from the root .env file
load_dotenv(dotenv_path=env_path)

def format_citation(metadata: dict) -> str:
    """Format citation from metadata"""
    file_name = metadata.get('file_name', 'unknown')
    page_range = metadata.get('page_range', 'unknown')
    return f"[{file_name}, pages: {page_range}]"

async def rag_pipeline(document_store, query: str, messages: List[dict] = None, previous_chunks: List[str] = None, model: str = None) -> AsyncGenerator[str, None]:
    """
    Async RAG pipeline with proper streaming
    
    Args:
        document_store: The document store instance
        query: The user's question
        messages: Optional list of previous chat messages
        previous_chunks: Optional list of previous context chunks
        model: Optional model name to use for generation
    """
    # Get new relevant chunks with distance threshold
    distance_threshold = float(os.getenv("DISTANCE_THRESHOLD", 0.6))
    n_results = int(os.getenv("N_RESULTS", 5))
    results = document_store.query_documents(
        query=query,
        n_results=n_results, 
        distance_threshold=distance_threshold
    )
    
    # Format chunks with citations
    current_chunks = []
    if results['documents'] and results['documents'][0]:
        for chunk, metadata in zip(results['documents'][0], results['metadatas'][0]):
            citation = format_citation(metadata)
            current_chunks.append(f"{chunk} {citation}")
    
    # Combine with previous context if available
    all_chunks = current_chunks
    if previous_chunks:
        all_chunks = list(set(current_chunks + previous_chunks))  # Remove duplicates
    
    # Create the system message - different versions based on available context
    if all_chunks:
        combined_context = "\n\n".join(all_chunks)
        context_section = f"### CONTEXT ###\n{combined_context}"
    else:
        context_section = "No relevant documentation found for this query."

    system_message = {
        "role": "system",
        "content": f"""**RAG Assistant Guidelines**
   1. Analyze the context thoroughly before answering
   2. Use ONLY verified information from provided documents
   3. If information is missing or no relevant documentation is found, clearly state "This is not covered in my documentation"
   4. When using information, ALWAYS include citations after each claim using the provided [filename, pages: X-Y] format
   5. Format response with:
      - Clear headings using ###
      - Bullet points for lists
      - Code blocks where applicable
      - Citations immediately after each claim
   6. Consider the conversation history for context and maintain consistency

   {context_section}"""
    }

    # Build the conversation history
    prompt = [system_message]
    
    if messages:
        # Add previous conversation history
        prompt.extend(messages)
    
    # Add the current query
    prompt.append({
        "role": "user",
        "content": query
    })

    ollama_api = OllamaAPI()
    # Use provided model or fall back to environment variable
    model_to_use = model or os.getenv("OLLAMA_MODEL", "")

    async for token in ollama_api.chat(prompt, model=model_to_use):
        yield token
