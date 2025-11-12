# query.py
"""
Queries the local FAISS vector database built from financial adviser documents.
It embeds a user query, retrieves the most relevant chunks, and (optionally)
uses an LLM to generate an answer grounded in those documents.
"""

import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from dotenv import load_dotenv

# ---------- CONFIG ----------
INDEX_DIR = "embeddings/wealth_kb_index"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"   # or gpt-4-turbo, gpt-3.5-turbo, etc.
TOP_K = 3                   # Number of relevant chunks to retrieve
# ----------------------------
load_dotenv()

def load_vectorstore():
    """Load the saved FAISS index."""
    if not os.path.exists(INDEX_DIR):
        raise FileNotFoundError(
            f"❌ No FAISS index found at '{INDEX_DIR}'. Run ingest.py first."
        )

    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    print("📦 Loading FAISS index...")
    vectorstore = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    print("✅ Index loaded successfully.")
    return vectorstore


def query_vectorstore(vectorstore, query, top_k=TOP_K):
    """Retrieve the most relevant chunks for a given query."""
    print(f"🔍 Searching for: '{query}'")
    results = vectorstore.similarity_search_with_score(query, k=top_k)

    print(f"\n📚 Top {top_k} results:\n")
    for i, (doc, score) in enumerate(results, 1):
        print(f"--- Result {i} (score={score:.4f}) ---")
        print(f"Source: {doc.metadata.get('source', 'N/A')}")
        print(f"Content: {doc.page_content[:400]}...\n")
    return results


def generate_answer(query, retrieved_docs):
    """Optionally, use an LLM to generate an answer based on retrieved docs."""
    llm = ChatOpenAI(model=LLM_MODEL)
    context = "\n\n".join([doc.page_content for doc, _ in retrieved_docs])

    prompt = f"""
You are a professional financial adviser assistant.
Answer the user's question using the context below.
Use only the context to answer questions. Do not rely on your own parametric memory.

Context:
{context}

Question: {query}
Answer:
"""
    response = llm.invoke(prompt)
    print("\n💬 LLM Answer:\n")
    print(response.content)


if __name__ == "__main__":
    vectorstore = load_vectorstore()

    while True:
        query = input("\n❓ Enter your query (or 'exit' to quit): ")
        if query.lower() in ["exit", "quit"]:
            break

        retrieved_docs = query_vectorstore(vectorstore, query)

        use_llm = input("\n🤖 Generate an LLM answer? (y/n): ").lower().startswith("y")
        if use_llm:
            generate_answer(query, retrieved_docs)
