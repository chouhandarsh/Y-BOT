from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel,RunnablePassthrough
from langchain_huggingface import ChatHuggingFace,HuggingFaceEndpoint
llm = HuggingFaceEndpoint(repo_id="meta-llama/Llama-3.1-8B-Instruct")
model= ChatHuggingFace(llm=llm)
parser = StrOutputParser()
def format_docs(docs):
    return "\n\n".join(
        doc.page_content
        for doc in docs
    )
def rag_chain(retriver):
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the question using only the provided context. The Answer must be from the given context and add answer like human in chat format
        Add some humanized context for felling that the conversation feels real
        Guidelines:
            1. Provide a direct, final answer to the user's question based on the context.
            2. Maintain a warm, natural, and humanized conversational tone.
            3. CRITICAL: Do NOT generate mock dialogue transcripts, fake chat logs, or prefixes like "You:" and
        Context:
        {context}

        Question:
        {question}
        

        If the answer is not present in the context,
        say that the information is not available
        in the video.
        """
    )
    chain =  RunnableParallel({
        "context":retriver|format_docs,
        "question":RunnablePassthrough()
    })|prompt|model|parser
    return chain

