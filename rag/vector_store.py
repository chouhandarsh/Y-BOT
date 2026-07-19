from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def create_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings()
    vector_store = FAISS.from_texts(chunks, embeddings)
    return vector_store