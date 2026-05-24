from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from app.rag.loader import load_knowledge_base, split_documents
import os

# Use free local embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def get_vectorstore():
    persist_directory = "chroma_db"
    
    # Load and process documents only if vectorstore doesn't exist
    if not os.path.exists(persist_directory) or len(os.listdir(persist_directory)) == 0:
        print("🔄 Building new vector database...")
        documents = load_knowledge_base()
        chunks = split_documents(documents)
        
        if len(chunks) > 0:
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=persist_directory
            )
            print(f"✅ VectorStore created with {len(chunks)} chunks")
        else:
            print("⚠️  No PDFs found. VectorStore will be empty.")
            vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_directory)
    else:
        vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        print("✅ Loaded existing VectorStore")
    
    return vectorstore

# Global retriever
vectorstore = get_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

