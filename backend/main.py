from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.rag_pipeline import rag_pipeline
from app.document_store import ChromaDocStore
from typing import List, Dict, Any
import json
import uvicorn
from app.logger_config import get_logger, log_time

# Initialize logger
logger = get_logger(__name__)

# Initialize ChromaDB store
chroma_store = ChromaDocStore()

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    messages: List[Dict[str, str]] = []  # Chat history
    previous_chunks: List[str] = []  # Optional: Previous relevant chunks
    model: str | None = None  # Optional: Model name

@app.post("/query")
@log_time(logger)
async def query_service(request: QueryRequest):
    """
    Streaming endpoint with proper async handling
    """
    logger.info(f"Received query request with question: {request.question}")

    async def generate():
        try:
            # Start streaming immediately
            async for chunk in rag_pipeline(
                chroma_store, 
                request.question,
                request.messages,
                model=request.model
            ):
                if chunk:
                    message = json.dumps({"answer": chunk})
                    yield f"data: {message}\n\n"

        except Exception as e:
            logger.error(f"Error in query streaming: {str(e)}", exc_info=True)
            error_msg = json.dumps({"error": str(e)})
            yield f"event: error\ndata: {error_msg}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/config")
@log_time(logger)
async def get_config():
    logger.info("Fetching chunking configuration")
    return chroma_store.get_chunking_config()

@app.get("/documents")
@log_time(logger)
async def get_documents():
    logger.info("Fetching all documents")
    results = chroma_store.get_all_documents()
    logger.info(f"Retrieved {len(results)} documents")
    return results

@app.post("/documents/clear")
@log_time(logger)
async def clear_documents():
    try:
        logger.info("Attempting to clear all documents")
        success = chroma_store.clear_documents()
        if success:
            logger.info("Successfully cleared all documents")
            return {"status": "success", "message": "Documents cleared successfully"}
    except Exception as e:
        logger.error(f"Failed to clear documents: {str(e)}", exc_info=True)
        return {"status": "error", "message": f"Failed to clear documents: {str(e)}"}
    logger.error("Failed to clear documents: Unknown error")
    return {"status": "error", "message": "Failed to clear documents"}

@app.post("/documents/upload")
@log_time(logger)
async def upload_documents(files: List[UploadFile] = File(...)):
    logger.info(f"Received {len(files)} files for upload")
    for file in files:
        logger.debug(f"File details - name: {file.filename}, content_type: {file.content_type}, size: {file.size if hasattr(file, 'size') else 'unknown'}")
    
    all_documents = []
    errors = []
    
    for file in files:
        try:
            # Process the file content
            documents = await chroma_store.extract_text_from_document(file)
            if documents:
                all_documents.extend(documents)
                logger.info(f"Successfully processed {file.filename}")
            else:
                errors.append(f"No documents extracted from {file.filename}")
        except Exception as e:
            error_msg = f"Error processing {file.filename}: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        finally:
            # Ensure we close the file
            await file.close()
    
    if not all_documents:
        error_summary = "\n".join(errors)
        return {
            "status": "error", 
            "message": f"No documents were successfully processed. Errors:\n{error_summary}"
        }
    
    # Process the successful documents
    processed_docs = []
    processed_metas = []
    
    for doc in all_documents:
        chunks = chroma_store.text_splitter.split_text(doc['text'])
        # Calculate page range for each chunk
        for j, chunk in enumerate(chunks):
            processed_docs.append(chunk)
            # Ensure all metadata fields have valid values
            metadata = {
                'source': str(doc.get('file_name', 'unknown')),
                'type': doc.get('file_type', 'unknown'),  # Use file_type from document
                'file_name': str(doc.get('file_name', 'unknown')),
                'page_number': str(doc.get('page_number', 'unknown')),
                'page_range': f"{doc.get('page_number', 'unknown')}",
                'chunk_num': str(j + 1),
                'total_chunks': str(len(chunks))
            }
            processed_metas.append(metadata)
    
    success = chroma_store.add_documents(processed_docs, processed_metas)
    if success:
        logger.info(f"Successfully added {len(processed_docs)} chunks to the database")
        return {"status": "success", "message": f"Successfully processed {len(files)} files"}
    else:
        logger.error("Failed to add documents to database")
        return {"status": "error", "message": "Failed to add documents to database"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)