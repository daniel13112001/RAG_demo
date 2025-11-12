# ingest.py
"""
Builds a local vector database from financial adviser documents.
It parses PDF, DOCX, PPTX, HTML, and TXT files, splits them into chunks,
creates embeddings, and stores them in a FAISS index.
"""

import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredFileLoader,
    UnstructuredHTMLLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

# ---------- CONFIG ----------
DATA_DIR = "data"  # Folder containing your docs
INDEX_DIR = "embeddings/wealth_kb_index"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "text-embedding-3-small"
# ----------------------------

load_dotenv()

def load_documents(data_dir):
    """Load all supported files from the data directory."""
    loaders = {
        ".pdf": PyPDFLoader,
        ".txt": UnstructuredFileLoader,
        ".html": UnstructuredHTMLLoader,
        ".docx": UnstructuredWordDocumentLoader,
        ".pptx": UnstructuredPowerPointLoader,
    }

    docs = []
    for file in os.listdir(data_dir):
        path = os.path.join(data_dir, file)
        ext = os.path.splitext(file)[1].lower()

        loader_cls = loaders.get(ext)
        if not loader_cls:
            print(f"⚠️ Skipping unsupported file: {file}")
            continue

        print(f"📄 Loading {file} ...")
        loader = loader_cls(path)
        try:
            loaded_docs = loader.load()
            for d in loaded_docs:
                d.metadata["source"] = file
            docs.extend(loaded_docs)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")

    print(f"✅ Loaded {len(docs)} documents.")
    return docs


def split_documents(docs):
    """Split large documents into smaller chunks."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️  Split into {len(chunks)} chunks.")
    return chunks


def embed_and_store(chunks):
    """Generate embeddings and store them in FAISS."""
    print("🔢 Generating embeddings...")
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)

    print("💾 Creating FAISS index...")
    vectorstore = FAISS.from_documents(chunks, embeddings)

    os.makedirs(os.path.dirname(INDEX_DIR), exist_ok=True)
    vectorstore.save_local(INDEX_DIR)
    print(f"✅ Vector DB saved to '{INDEX_DIR}'.")


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    if not docs:
        print("No documents found. Please place files in the 'data/' folder.")
    else:
        chunks = split_documents(docs)
        embed_and_store(chunks)
