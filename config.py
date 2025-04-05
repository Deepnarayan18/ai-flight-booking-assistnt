import os
from dotenv import load_dotenv
import streamlit as st
from groq import Groq
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

def load_config():
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        st.error("Error: GROQ_API_KEY not found in .env file!")
        return None
    return api_key

def initialize_llm(api_key):
    client = Groq(api_key=api_key)
    llm = ChatGroq(groq_api_key=api_key, model_name="deepseek-r1-distill-llama-70b")
    prompt = PromptTemplate(
        input_variables=["context"],
        template="""
        You are a professional flight booking assistant. Assist users in booking flights by collecting details like departure city, destination, travel date, airline, seating class, name, and email step-by-step. Use the context to track progress and respond in ONE SHORT LINE. Avoid hallucination—stick to provided details and dataset flights strictly. If input is unclear, ask for clarification briefly.
        Context: {context}
        Response:
        """
    )
    return LLMChain(llm=llm, prompt=prompt, memory=ConversationBufferMemory(), verbose=True)