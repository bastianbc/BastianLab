from django.shortcuts import render
from django.contrib.auth.decorators import login_required,permission_required
from core.decorators import permission_required_for_async
from django.http import JsonResponse
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.document_loaders import UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
import os

def train_story_documents(request):
    open_ai_key = os.environ["OPENAI_API_KEY"]
    print(open_ai_key)

    for root, dirs, files in os.walk("/Users/cbagci/Library/CloudStorage/Box-Box/LabDB development/Stories"):
        for fname in files:
            print(fname)

    loader = UnstructuredFileLoader("your_file.docx")
    docs = loader.load()

    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    splits = text_splitter.split_documents(docs)

    # Create FAISS vector store
    vectorstore = FAISS.from_documents(splits, OpenAIEmbeddings())

    # Save for later use
    vectorstore.save_local("/Users/cbagci/Library/CloudStorage/Box-Box/LabDB development/GPT")

    retriever = vectorstore.as_retriever()
    qa_chain = RetrievalQA.from_chain_type(llm=OpenAI(), retriever=retriever)

    response = qa_chain.run("How To Extract nucleic acids?")
    print(response)



