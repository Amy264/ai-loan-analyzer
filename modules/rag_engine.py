"""
RAG Engine Module
Retrieval-Augmented Generation engine for context-aware loan analysis using Chroma.
"""

import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv
import warnings
from .prompt_loader import load_prompt

load_dotenv()


class RAGEngine:
    """Retrieval-Augmented Generation engine for loan document analysis using Chroma."""

    def __init__(self, collection_name: str = "loan_documents", persist_dir: str = "./chroma_db"):
        """
        Initialize the RAG engine with Chroma vector database.
        
        Args:
            collection_name (str): Name of the Chroma collection
            persist_dir (str): Directory to persist Chroma database
        """
        self.collection_name = collection_name
        self.persist_dir = persist_dir
        self.documents = []
        self.embeddings = None
        self.vectorstore = None
        self.llm = None
        
        # Initialize embeddings using OpenAI via OpenRouter
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable not set")
        
        try:
            self.embeddings = OpenAIEmbeddings(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                model="text-embedding-3-small"
            )
            
            # Initialize Chroma vector store
            self.vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                persist_directory=persist_dir
            )
        except Exception as e:
            error_msg = str(e)
            if "getaddrinfo failed" in error_msg or "Failed to resolve" in error_msg:
                warnings.warn(
                    "⚠️ No internet connection detected. Vector database features may be limited. "
                    "Please check your internet connection or the embedding service.",
                    RuntimeWarning
                )
                # Initialize with dummy embeddings to allow basic operation
                self.vectorstore = None
            else:
                raise
        
        # Initialize LLM for response generation
        self.llm = ChatOpenAI(
            model="openrouter/auto",
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def add_documents(self, texts: list, metadatas: list = None):
        """
        Add documents to the vector database.
        
        Args:
            texts (list): List of text content to add
            metadatas (list): List of metadata dictionaries for each text
            
        Returns:
            list: Document IDs
        """
        if metadatas is None:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        # Split documents into chunks
        docs = []
        for i, text in enumerate(texts):
            chunks = self.text_splitter.split_text(text)
            for j, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        **metadatas[i],
                        "chunk": j,
                        "document_index": i
                    }
                )
                docs.append(doc)
        
        self.documents.extend(docs)
        
        # Add to vector store if available
        if self.vectorstore is None:
            warnings.warn(
                "⚠️ Vector database not available (no internet connection). "
                "Documents stored in memory but vector search not available.",
                RuntimeWarning
            )
            return [f"doc_{i}" for i in range(len(docs))]
        
        try:
            ids = self.vectorstore.add_documents(docs)
            return ids
        except Exception as e:
            if "getaddrinfo failed" in str(e) or "Failed to resolve" in str(e):
                warnings.warn(
                    "⚠️ Network connection lost during document indexing. "
                    "Documents stored but vector search may be unavailable.",
                    RuntimeWarning
                )
                return [f"doc_{i}" for i in range(len(docs))]
            raise

    def retrieve_context(self, query: str, top_k: int = 5):
        """
        Retrieve relevant documents based on a query.
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
            
        Returns:
            list: Retrieved relevant documents
        """
        if self.vectorstore is None:
            # Fallback: simple text search in stored documents
            matching_docs = []
            query_lower = query.lower()
            for doc in self.documents[:top_k]:
                if query_lower in doc.page_content.lower():
                    matching_docs.append(doc)
            return matching_docs if matching_docs else self.documents[:top_k]
        
        try:
            results = self.vectorstore.similarity_search(query, k=top_k)
            return results
        except Exception as e:
            if "getaddrinfo failed" in str(e) or "Failed to resolve" in str(e):
                # Fallback to simple text search
                warnings.warn(
                    "⚠️ Vector search unavailable. Using basic text search instead.",
                    RuntimeWarning
                )
                matching_docs = []
                query_lower = query.lower()
                for doc in self.documents[:top_k]:
                    if query_lower in doc.page_content.lower():
                        matching_docs.append(doc)
                return matching_docs if matching_docs else self.documents[:top_k]
            raise

    def generate_response(self, query: str, context: list):
        """
        Generate a response based on retrieved context.
        
        Args:
            query (str): User query
            context (list): Retrieved context documents
            
        Returns:
            str: Generated response
        """
        # Format context
        context_text = "\n\n".join([doc.page_content for doc in context])
        
        # Load prompt from external file
        prompt_template = load_prompt("prompts/rag_response.txt")
        prompt = PromptTemplate(
            input_variables=["context", "query"],
            template=prompt_template
        )
        
        formatted_prompt = prompt.format(context=context_text, query=query)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def query(self, query: str, top_k: int = 5):
        """
        Query the vector database and generate a response.
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to use for context
            
        Returns:
            dict: Dictionary containing context documents and generated response
        """
        # Retrieve relevant context
        context = self.retrieve_context(query, top_k)
        
        if not context:
            return {
                "context": [],
                "response": "No relevant documents found for this query."
            }
        
        # Generate response based on context
        response = self.generate_response(query, context)
        
        return {
            "context": [doc.page_content for doc in context],
            "response": response
        }

    def index_documents(self):
        """
        Create embeddings and index documents for efficient retrieval.
        
        Returns:
            bool: True if indexing was successful
        """
        if not self.documents:
            return False
        
        if self.vectorstore is None:
            # Documents are in memory only
            return True
        
        try:
            # Documents are already indexed when added
            # Note: Newer versions of Chroma persist automatically
            if hasattr(self.vectorstore, 'persist'):
                self.vectorstore.persist()
            return True
        except AttributeError:
            # Newer Chroma versions persist automatically
            return True
        except Exception as e:
            if "getaddrinfo failed" in str(e) or "Failed to resolve" in str(e):
                # Network error but documents are still in memory
                warnings.warn(
                    "⚠️ Could not persist vector database due to network issue. "
                    "Documents cached in memory.",
                    RuntimeWarning
                )
                return True
            print(f"Error indexing documents: {str(e)}")
            return False

    def clear_collection(self):
        """
        Clear all documents from the collection.
        
        Returns:
            bool: True if successful
        """
        try:
            self.documents = []
            if self.vectorstore is not None:
                self.vectorstore.delete_collection()
                self.vectorstore = Chroma(
                    collection_name=self.collection_name,
                    embedding_function=self.embeddings,
                    persist_directory=self.persist_dir
                )
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False

    def get_collection_info(self):
        """
        Get information about the current collection.
        
        Returns:
            dict: Collection statistics
        """
        try:
            if self.vectorstore is None:
                count = len(self.documents)
            else:
                count = self.vectorstore._collection.count()
            
            return {
                "collection_name": self.collection_name,
                "total_documents": count,
                "persist_directory": self.persist_dir,
                "vector_db_available": self.vectorstore is not None
            }
        except Exception as e:
            return {
                "error": str(e),
                "total_documents": len(self.documents),
                "vector_db_available": False
            }
