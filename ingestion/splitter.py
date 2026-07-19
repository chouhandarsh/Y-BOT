from langchain_text_splitters import RecursiveCharacterTextSplitter
class Splitter:
    @staticmethod
    def split(docs):
        splitter=RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=150
        )
        return splitter.split_text(docs)