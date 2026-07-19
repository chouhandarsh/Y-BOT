# Y-BOT 🎥🤖

**Y-BOT** is a Retrieval-Augmented Generation (RAG) chatbot that lets you ask questions about a video and get answers grounded directly in the video's transcript — no hallucinated guesses, just retrieved context.

> Ask anything — every answer is retrieved straight out of the video, not guessed.

Built with **LangChain**, **HuggingFace embeddings**, and **HuggingFace-hosted LLMs (ChatHuggingFace)**, with two interchangeable front-ends: **Chainlit** and **Streamlit**.

---

## ✨ Features

- 🔎 **Video transcript ingestion** — loads and prepares video content for retrieval
- ✂️ **Smart chunking** — splits transcripts into overlapping chunks using `RecursiveCharacterTextSplitter` for better context preservation
- 🧠 **HuggingFace embeddings** — converts chunks into vector representations
- 🗂️ **Vector store retrieval (RAG)** — retrieves only the most relevant chunks for a given question
- 💬 **ChatHuggingFace integration** — generates grounded answers using a HuggingFace-hosted chat model
- 🖼️ **Thumbnail support** — displays video thumbnails alongside chat responses

---

## 📁 Project Structure

```
Y_BOT/
├── assets/
│   └── image.png              # UI / branding image
├── ingestion/
│   ├── loader.py               # Loads video/transcript data
│   └── splitter.py             # Chunks text using RecursiveCharacterTextSplitter
├── rag/                         # Retrieval-augmented generation pipeline
│   ├── (embeddings, vector store, retriever logic)
├── .chainlit/                   # Chainlit configuration
├── .files/                      # Chainlit runtime/session files
├── venv/                        # Python virtual environment
├── chainlit.md                  # Chainlit welcome/landing page content
├── history.txt                  # Chat/session history log
├── learn.ipynb                  # Notebook for experimentation/prototyping
├── main.py                      # Chainlit app entry point
├── main2.py                     # Streamlit app entry point
├── test.py                      # Test script
└── requirements.txt             # Python dependencies
```

---

## 🛠️ Tech Stack

| Component        | Technology                              |
|-------------------|------------------------------------------|
| Orchestration     | LangChain                               |
| Chunking          | `langchain-text-splitters` (`RecursiveCharacterTextSplitter`) |
| Embeddings        | HuggingFace Embeddings                  |
| LLM               | `ChatHuggingFace` (HuggingFace Inference)|
| Vector Store      | FAISS / Chroma (via `rag/`)             |                            |
| UI (Option 2)     | Streamlit                               |
| Language          | Python 3                                |

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/Y_BOT.git
   cd Y_BOT
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   > ⚠️ If you hit `ModuleNotFoundError: No module named 'langchain_text_splitters'`, install it explicitly:
   > ```bash
   > pip install langchain-text-splitters
   > ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   HUGGINGFACEHUB_API_TOKEN=your_hf_token_here
   ```

---

## 🚀 Usage

### Streamlit UI
```bash
streamlit run main2.py
```

Then open the local URL shown in the terminal (typically `http://localhost:8501` for Streamlit or `http://localhost:8000` for Chainlit).

---

## 🧩 How It Works

1. **Ingestion** (`ingestion/loader.py`) — Loads the video/transcript source data.
2. **Chunking** (`ingestion/splitter.py`) — Splits the transcript into overlapping chunks using `RecursiveCharacterTextSplitter` so context isn't lost at chunk boundaries.
3. **Embedding** — Each chunk is embedded using a HuggingFace embedding model.
4. **Retrieval** (`rag/`) — On a user query, the most semantically relevant chunks are retrieved from the vector store.
5. **Generation** — The retrieved chunks + user question are passed to `ChatHuggingFace`, which generates an answer grounded strictly in the retrieved context.
6. **Display** — The UI (Chainlit or Streamlit) renders the answer, optionally alongside the video thumbnail.

---

## 🐞 Known Issues / Notes

- Ensure `langchain-text-splitters` is installed separately — newer LangChain versions moved text splitters into their own package.
- Streamlit's `use_container_width` parameter is deprecated (removal after 2025-12-31) — use `width='stretch'` or `width='content'` instead.

---

## 🗺️ Roadmap

- [ ] Add support for multiple video sources in a single session
- [ ] Cache embeddings to avoid recomputation on repeated runs
- [ ] Add source-chunk highlighting in the UI for transparency
- [ ] Dockerize the app for easier deployment

---

## 📄 License

This project is currently unlicensed. Add a `LICENSE` file to specify usage terms.

---

## 🙋 Author

Built by **Darsh Chouhan** ([@chouhandarsh](https://github.com/chouhandarsh))
