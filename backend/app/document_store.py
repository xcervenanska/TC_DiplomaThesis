import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
from .logger_config import get_logger, log_time
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from markitdown import MarkItDown
import mimetypes
import asyncio
from io import BytesIO
from pdfminer.high_level import extract_text as pdf_extract_text
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

# Get the project root directory (where .env is located)
root_dir = Path(__file__).resolve().parents[2]  # Go up 2 levels from document_store.py
env_path = root_dir / '.env'

# Load the environment variables from the root .env file
load_dotenv(dotenv_path=env_path)

logger = get_logger(__name__)

logger.info(f"Loading environment variables from: {env_path}")
logger.debug(f"CHUNK_SIZE: {os.getenv('CHUNK_SIZE')}")
logger.debug(f"CHUNK_OVERLAP: {os.getenv('CHUNK_OVERLAP')}")

class ChromaDocStore:
    def __init__(self):
        self.settings = Settings(
            allow_reset=os.getenv('CHROMA_ALLOW_RESET', 'true').lower() == 'true',
            anonymized_telemetry=os.getenv('CHROMA_ANONYMIZED_TELEMETRY', 'false').lower() == 'true',
            is_persistent=os.getenv('CHROMA_IS_PERSISTENT', 'true').lower() == 'true'
        )
        
        self.client = chromadb.Client(self.settings)
        self.collection_name = "documents"
        
        # Load configuration from environment variables
        self.n_results = int(os.getenv('N_RESULTS', 5))
        self.distance_threshold = float(os.getenv('DISTANCE_THRESHOLD', 1.5))

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function
        )
        
        self.chunk_size = int(os.getenv('CHUNK_SIZE', 1000))
        self.chunk_overlap = int(os.getenv('CHUNK_OVERLAP', 200))
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n##", "\n\n", "\n", ". ", " ", ""]
        )
        logger.info(f"Initialized ChromaDocStore with chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}")

    @staticmethod
    def extract_text_from_pdf(file_obj) -> list:
        """
        Extract text from a PDF file using pdfminer.six, returning a list of page texts.
        Each element in the list corresponds to text extracted from a page.
        """
        resource_manager = PDFResourceManager()
        laparams = LAParams()
        codec = 'utf-8'
        page_texts = []

        for page_number, page in enumerate(PDFPage.get_pages(file_obj, check_extractable=True), start=1):
            output_string = StringIO()
            converter = TextConverter(resource_manager, output_string, codec=codec, laparams=laparams)
            interpreter = PDFPageInterpreter(resource_manager, converter)
            try:
                interpreter.process_page(page)
                text = output_string.getvalue()
                page_texts.append(text)
            finally:
                converter.close()
                output_string.close()

        return page_texts

    @staticmethod
    async def extract_text_from_document(file_obj) -> List[Dict[str, any]]:
        """
        Extract text from a document, handling PDFs with pdfminer.six and other formats with MarkItDown.
        """
        try:
            # Get the file name from the file object
            file_name = getattr(file_obj, 'filename', None) or getattr(file_obj, 'name', 'unknown')
            file_type = mimetypes.guess_type(file_name)[0]

            logger.info(f"Processing document: {file_name} (type: {file_type})")

            if not file_type:
                logger.warning(f"Could not determine file type for {file_name}, attempting conversion anyway")

            # Read the file content if it's a FastAPI UploadFile
            if hasattr(file_obj, 'read'):
                logger.debug("Reading file content...")
                if asyncio.iscoroutinefunction(file_obj.read):
                    file_content = await file_obj.read()
                else:
                    file_content = file_obj.read()

                logger.debug(f"Read {len(file_content)} bytes from file")

                # Convert to file-like object
                file_obj = BytesIO(file_content)
                file_obj.seek(0)  # Ensure we're at the start of the stream
                logger.debug("Converted to BytesIO object")

            # Handle PDF files separately using pdfminer
            if file_type == 'application/pdf':
                logger.info("Detected PDF file, using pdfminer to extract text.")
                try:
                    page_texts = ChromaDocStore.extract_text_from_pdf(file_obj)  # Now returns a list of texts per page
                    if not page_texts or all(not text.strip() for text in page_texts):
                        raise ValueError("pdfminer extracted empty text content")
                    documents = []
                    for i, text in enumerate(page_texts, start=1):
                        if text.strip():
                            documents.append({
                                'text': text,
                                'page_number': i,  # Set page number dynamically
                                'file_name': file_name,
                                'file_type': file_type
                            })
                    if not documents:
                        raise ValueError("No non-empty pages extracted from PDF")
                    logger.info(f"Successfully extracted PDF with {len(documents)} pages from {file_name}")
                    return documents
                except Exception as pdf_error:
                    logger.error(f"pdfminer extraction error: {str(pdf_error)}", exc_info=True)
                    raise ValueError(f"PDF extraction failed: {str(pdf_error)}")

            # Initialize and configure MarkItDown for non-PDF files
            logger.debug("Initializing MarkItDown for non-PDF file...")
            md = MarkItDown()

            # Convert document to markdown
            logger.debug("Starting document conversion with MarkItDown...")
            try:
                result = md.convert(file_obj)
                logger.debug("Document conversion completed")


                if not result:
                    raise ValueError("MarkItDown returned None result")

                if not hasattr(result, 'text_content'):
                    raise ValueError("MarkItDown result missing text_content attribute")

                if not result.text_content:
                    raise ValueError("MarkItDown extracted empty text content")

                logger.debug(f"Text content length: {len(result.text_content)}")
                logger.debug(f"First 100 chars: {result.text_content[:100]}")

            except Exception as conv_error:
                logger.error(f"MarkItDown conversion error: {str(conv_error)}", exc_info=True)
                raise ValueError(f"Document conversion failed: {str(conv_error)}")

            # Create document entry
            documents = [{
                'text': result.text_content,
                'page_number': 1,
                'file_name': file_name,
                'file_type': file_type or 'unknown'
            }]

            logger.info(f"Successfully extracted {len(result.text_content)} characters from {file_name}")
            return documents

        except Exception as e:
            logger.error(f"Error extracting text from document {file_name}: {str(e)}", exc_info=True)
            raise


    @log_time(logger)
    def add_documents(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str] = None) -> bool:
        try:
            # Validate input lengths match
            if len(documents) != len(metadatas):
                raise ValueError(f"Number of documents ({len(documents)}) must match number of metadatas ({len(metadatas)})")

            # Get current collection size for ID generation
            current_docs = self.collection.get()
            start_idx = len(current_docs['ids']) if current_docs['ids'] else 0
            
            # Generate sequential IDs
            generated_ids = [f"doc_{i}" for i in range(start_idx, start_idx + len(documents))]
            
            # Ensure required metadata fields exist
            for metadata in metadatas:
                if 'file_name' not in metadata:
                    metadata['file_name'] = 'unknown'
                if 'page_range' not in metadata:
                    metadata['page_range'] = 'unknown'
            
            logger.info(f"Adding {len(documents)} documents with IDs {generated_ids[0]} to {generated_ids[-1]}")
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=generated_ids
            )
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def get_chunking_config(self):
        return {
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }

    def get_all_documents(self):
        return self.collection.get()

    @log_time(logger)
    def query_documents(self, query: str, n_results: int = None, distance_threshold: float = None):
        """
        Query documents with a distance threshold to filter out irrelevant results.
        Lower distance means more similar (better match). Range is typically 0-1.
        
        Args:
            query (str): The query text to search for
            n_results (int, optional): Number of results to return. Defaults to self.n_results
            distance_threshold (float, optional): Maximum distance threshold for results. Defaults to self.distance_threshold
        """
        if n_results is None:
            n_results = self.n_results
        
        if distance_threshold is None:
            distance_threshold = self.distance_threshold
            
        logger.info(f"Querying documents with: {query[:100]}...")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Filter out results above the distance threshold if distances are available
        if results['documents'] and results['documents'][0]:
            # Check if distances are available in results
            if 'distances' in results and results['distances'][0]:
                filtered_indices = [
                    i for i, dist in enumerate(results['distances'][0]) 
                    if dist <= distance_threshold
                ]
                
                # If no documents pass the threshold, return empty results
                if not filtered_indices:
                    logger.info("No documents found within acceptable distance threshold")
                    return {
                        'documents': [[]],
                        'metadatas': [[]],
                        'distances': [[]] if 'distances' in results else None
                    }
                
                # Filter all result lists to only include relevant documents
                results['documents'][0] = [results['documents'][0][i] for i in filtered_indices]
                results['metadatas'][0] = [results['metadatas'][0][i] for i in filtered_indices]
                if 'distances' in results:
                    results['distances'][0] = [results['distances'][0][i] for i in filtered_indices]
            
            # Log retrieved chunks and their distances
            for i in range(len(results['documents'][0])):
                distance = results['distances'][0][i] if 'distances' in results else 'N/A'
                metadata = results['metadatas'][0][i]
                logger.info(f"Retrieved chunk {i + 1}/{len(results['documents'][0])}:")
                logger.info(f"  Distance: {distance}")
                logger.info(f"  Metadata: {metadata}")
                logger.info(f"  Content: {results['documents'][0][i][:50]}...")
        
        return results

    @log_time(logger)
    def clear_documents(self):
        logger.info("Clearing all documents and reinitializing collection")
        try:
            # Delete the entire collection
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            
            # Recreate the collection with the current embedding function
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"Recreated collection: {self.collection_name}")
            
            return True
        except Exception as e:
            logger.error(f"Error clearing documents: {e}")
            return False
