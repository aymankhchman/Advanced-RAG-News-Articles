import pandas as pd
import numpy as np
import json
from datetime import datetime
import inspect


from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEndpoint, HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate

class LLMSummarizer:

    def __init__(self, embedding_model: str, llm_info: dict,
                data_path: str, prompt_template: str,
                ):
        self.embedding_model = embedding_model
        self.llm = HuggingFaceEndpoint(**llm_info)
        self.data_path = data_path
        self.prompt_template = prompt_template
        self.rag_built = False


    def _load_embedding_model(self):
        return  HuggingFaceEmbeddings(model_name=self.embedding_model)
    
    def _retriever(self):

        loader = CSVLoader(file_path=self.data_path)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=self._load_embedding_model())

        return vectorstore.as_retriever(search_kwargs={"k": 20})
    
    def build_rag(self):
        custom_rag_prompt = PromptTemplate.from_template(self.prompt_template)
  
        self.rag_chain = (
            {"context": self._retriever() | LLMSummarizer.format_docs, "question": RunnablePassthrough()}
            | custom_rag_prompt
            | self.llm
            | StrOutputParser()
        )

    @staticmethod
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def ask(self, question):

        if not self.rag_built:
            self.build_rag()
        output = self.rag_chain.invoke(question)
        return inspect.cleandoc(output)

