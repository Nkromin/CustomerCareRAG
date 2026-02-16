"""
FAISS Vector Store Management
"""
import os
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import config


class VectorStoreManager:
    """
    Manages FAISS vector store for document retrieval
    """

    def __init__(self):
        self.embeddings = None
        self.vector_store = None
        self.retriever = None

    def initialize_embeddings(self):
        """Initialize HuggingFace embeddings"""
        print(f"🔧 Initializing embeddings: {config.EMBEDDING_MODEL}")

        self.embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )

        print("✓ Embeddings initialized")

    def create_vector_store(self, documents: List[Document]):
        """
        Create FAISS vector store from documents

        Args:
            documents: List of Document chunks
        """
        if not documents:
            print("⚠️  No documents to index")
            return

        if not self.embeddings:
            self.initialize_embeddings()

        print(f"🔨 Creating FAISS vector store with {len(documents)} chunks...")

        try:
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )

            # Create retriever with optimized parameters for semantic search
            # Note: We'll override search_kwargs in retrieve method when needed
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": 5,  # Return top 5 most relevant chunks by default
                    "fetch_k": 25  # Fetch more candidates before filtering
                }
            )

            print("✓ Vector store created successfully")

        except Exception as e:
            print(f"❌ Error creating vector store: {e}")
            raise

    def save_vector_store(self, path: str = config.VECTOR_STORE_PATH):
        """Save vector store to disk"""
        if self.vector_store:
            try:
                self.vector_store.save_local(path)
                print(f"✓ Vector store saved to: {path}")
            except Exception as e:
                print(f"⚠️  Could not save vector store: {e}")

    def load_vector_store(self, path: str = config.VECTOR_STORE_PATH):
        """Load vector store from disk"""
        if not os.path.exists(path):
            print(f"⚠️  Vector store not found at: {path}")
            return False

        try:
            if not self.embeddings:
                self.initialize_embeddings()

            print(f"📂 Loading vector store from: {path}")
            self.vector_store = FAISS.load_local(
                path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )

            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            print("✓ Vector store loaded successfully")
            return True

        except Exception as e:
            print(f"❌ Error loading vector store: {e}")
            return False

    def retrieve(self, query: str, k: int = 5) -> List[Document]:
        """
        Retrieve relevant documents for a query using semantic similarity

        Args:
            query: Search query
            k: Number of documents to return (default: 5 for better semantic coverage)

        Returns:
            List of relevant documents
        """
        if not self.vector_store:
            print("⚠️  Vector store not initialized")
            return []

        try:
            # Use similarity_search directly to respect k parameter
            docs = self.vector_store.similarity_search(query, k=k)
            return docs

        except Exception as e:
            print(f"❌ Error retrieving documents: {e}")
            return []

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        """
        Direct similarity search

        Args:
            query: Search query
            k: Number of results

        Returns:
            List of similar documents
        """
        if not self.vector_store:
            return []

        return self.vector_store.similarity_search(query, k=k)


def initialize_vector_store(force_rebuild: bool = False) -> VectorStoreManager:
    """
    Initialize or load vector store

    Args:
        force_rebuild: Force rebuild from documents

    Returns:
        VectorStoreManager instance
    """
    manager = VectorStoreManager()

    # Try to load existing vector store
    if not force_rebuild and manager.load_vector_store():
        return manager

    # Build new vector store
    print("🔄 Building new vector store from documents...")
    from rag.loader import load_documents, split_documents

    documents = load_documents()
    chunks = split_documents(documents)

    if chunks:
        manager.create_vector_store(chunks)
        manager.save_vector_store()
    else:
        print("⚠️  No documents to index")

    return manager

