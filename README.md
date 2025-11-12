# RAG Financial Adviser Assistant

A simple Retrieval-Augmented Generation (RAG) system for financial advice with a web UI.

## 📋 Project Structure

```
RAG_demo/
├── ingest.py              # Build vector database from documents
├── query.py               # Command-line query tool
├── app.py                 # Flask server with REST API
├── templates/
│   └── index.html         # Web UI
├── static/
│   ├── style.css          # Styling
│   └── script.js          # Frontend logic
├── data/                  # Your financial documents (PDF, DOCX, HTML, TXT, PPTX)
├── embeddings/
│   └── wealth_kb_index/   # FAISS vector database
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root with:

```
OPENAI_API_KEY=your-api-key-here
```

### 3. Ingest Documents (First Time Only)

Place your financial documents (PDF, DOCX, HTML, TXT, PPTX) in the `data/` folder, then:

```bash
python ingest.py
```

You should see output like:
```
📄 Loading Client_Onboarding_Notes.txt ...
📄 Loading Market_Risk_Education.html ...
✅ Loaded 45 documents.
✂️  Split into 120 chunks.
🔢 Generating embeddings...
💾 Creating FAISS index...
✅ Vector DB saved to 'embeddings/wealth_kb_index'.
```

### 4. Start the Server

```bash
python app.py
```

You should see:
```
🚀 Starting Flask server on http://127.0.0.1:5000
```

### 5. Open the Web UI

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## 💬 How It Works

1. **User submits a question** via the web UI
2. **Backend retrieves relevant documents** from the FAISS vector database
3. **LLM generates an answer** using the retrieved context (using GPT-4o-mini)
4. **Response is displayed** with:
   - The LLM-generated answer
   - Sources used from your documents
   - Retrieved context chunks with relevance scores

## 🎯 Features

- ✅ Simple web interface for querying
- ✅ RAG pipeline with context injection
- ✅ Support for multiple document types (PDF, DOCX, HTML, TXT, PPTX)
- ✅ Relevance scoring for retrieved documents
- ✅ Source attribution
- ✅ Built with Flask + LangChain + OpenAI

## 📝 Configuration

Edit `app.py` or `query.py` to adjust:

- `CHUNK_SIZE`: Size of document chunks (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 100)
- `EMBEDDING_MODEL`: OpenAI embedding model (default: "text-embedding-3-small")
- `LLM_MODEL`: LLM to use (default: "gpt-4o-mini")
- `TOP_K`: Number of relevant chunks to retrieve (default: 3)

## 🛠️ Troubleshooting

**"No FAISS index found"**
- Run `python ingest.py` first to build the vector database

**"Cannot connect to server"**
- Make sure `python app.py` is running
- Check that port 5000 is available

**API errors**
- Ensure your `OPENAI_API_KEY` is set in `.env`
- Check that you have sufficient OpenAI API credits

## 📚 Next Steps

- Add more documents to `data/` and re-run `ingest.py`
- Customize the UI styling in `static/style.css`
- Modify system prompts in `app.py` for different use cases
- Deploy to cloud (Heroku, AWS, etc.)

---

**Created**: November 2025
**Tech Stack**: Flask, LangChain, OpenAI, FAISS, HTML/CSS/JavaScript
