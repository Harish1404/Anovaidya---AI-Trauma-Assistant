from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.config import settings
import os

def load_knowledge_base():
    """Load all PDFs from knowledge_base folder"""
    folder_path = "knowledge_base"
    
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"📁 Created {folder_path} folder. Please add PDFs there.")
        return []
    
    loader = PyPDFDirectoryLoader(folder_path)
    documents = loader.load()
    
    print(f"✅ Loaded {len(documents)} PDF documents")
    return documents


def split_documents(documents):
    """Split documents into chunks"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = text_splitter.split_documents(documents)
    print(f"✅ Split into {len(chunks)} chunks")
    return chunks


