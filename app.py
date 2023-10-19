import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

import requests


model_id = "sentence-transformers/all-MiniLM-L6-v2"
hf_token = "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"

api_url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model_id}"
headers = {"Authorization": f"Bearer {hf_token}"}


def get_conversation_chain(vector_store):
    llm = llm = HuggingFaceHub(
        repo_id="mistralai/Mistral-7B-v0.1",
        model_kwargs={"temperature": 0.5, "max_length": 64},
    )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=vector_store.as_retriever(), memory=memory
    )
    return conversation_chain


def get_vector_store(texts):
    embedding = HuggingFaceInstructEmbeddings(model_name=model_id)
    vector_store = FAISS.from_texts(texts=texts, embedding=embedding)
    return vector_store


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with multiple PDFs", page_icon=":books:")
    st.header("Chat with multiple PDFs :books:")

    st.text_input("Ask a question to your file:")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None

    with st.sidebar:
        st.subheader("Your files")
        pdf_docs = st.file_uploader("Upload files", accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                # extract the text from the pdfs
                raw_text = get_pdf_text(pdf_docs)

                # divide the text into chunks
                text_chunks = get_text_chunks(raw_text)

                # create vector store
                vector_store = get_vector_store(text_chunks)

                # create conversation chain
                st.session_state.conversation = get_conversation_chain(
                    vector_store=vector_store
                )


if __name__ == "__main__":
    main()
