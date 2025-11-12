# app.py
"""
Flask server for the RAG pipeline.
Provides a REST API endpoint for querying the knowledge base.
"""

import os
from flask import Flask, request, jsonify, render_template
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv

# ---------- CONFIG ----------
INDEX_DIR = "embeddings/wealth_kb_index"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TOP_K = 3
# ----------------------------

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")

# Global vectorstore (loaded once at startup)
vectorstore = None


def load_vectorstore():
    """Load the saved FAISS index."""
    global vectorstore
    if not os.path.exists(INDEX_DIR):
        raise FileNotFoundError(
            f"❌ No FAISS index found at '{INDEX_DIR}'. Run ingest.py first."
        )
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    print("📦 Loading FAISS index...")
    vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    print("✅ Index loaded successfully.")


def query_rag(user_query):
    """Query the vector store and generate an LLM answer."""
    # Retrieve relevant documents
    results = vectorstore.similarity_search_with_score(user_query, k=TOP_K)
    
    # Prepare context from retrieved documents
    context = "\n\n".join([doc.page_content for doc, _ in results])
    
    # Get sources for citation
    sources = list(set([doc.metadata.get("source", "Unknown") for doc, _ in results]))
    
    # Generate answer using LLM
    llm = ChatOpenAI(model=LLM_MODEL, temperature=0.7)
    
    prompt = f"""You are a professional financial adviser assistant.
Answer the user's question using the context below. Be helpful, accurate, and concise.

Context:
{context}

Question: {user_query}

Answer:"""
    
    response = llm.invoke(prompt)
    
    return {
        "answer": response.content,
        "sources": sources,
        "context_chunks": [
            {
                "content": doc.page_content[:300] + "...",
                "source": doc.metadata.get("source", "Unknown"),
                "score": float(score)
            }
            for doc, score in results
        ]
    }


@app.route("/")
def index():
    """Serve the main UI page."""
    return render_template("index.html")


@app.route("/api/query", methods=["POST"])
def api_query():
    """API endpoint for RAG queries."""
    try:
        data = request.json
        user_query = data.get("query", "").strip()
        
        if not user_query:
            return jsonify({"error": "Query cannot be empty"}), 400
        
        result = query_rag(user_query)
        return jsonify(result), 200
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "vectorstore_loaded": vectorstore is not None}), 200


if __name__ == "__main__":
    load_vectorstore()
    print("🚀 Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
