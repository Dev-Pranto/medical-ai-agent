import streamlit as st
from medical_agent import MedicalAIAgent
import sqlite3
import pandas as pd
import os

# Configure page
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if "agent" not in st.session_state:
    # Get API keys from Streamlit secrets or environment variables
    try:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
    except:
        # Fallback to environment variables
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not gemini_api_key:
        st.error("Please set GEMINI_API_KEY in your environment variables or Streamlit secrets")
        st.stop()
    
    try:
        st.session_state.agent = MedicalAIAgent(gemini_api_key, tavily_api_key)
        st.success("AI Agent initialized successfully!")
    except Exception as e:
        st.error(f"Failed to initialize AI Agent: {str(e)}")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
st.title("🏥 Medical AI Assistant")
st.markdown("Ask questions about medical datasets or general medical knowledge")

# Sidebar
with st.sidebar:
    st.header("About")
    st.markdown("""
    This AI assistant can help with:
    - Answering questions about medical datasets (Heart Disease, Cancer, Diabetes)
    - Providing general medical knowledge from web sources
    
    **Note:** The medical datasets need to be uploaded as CSV files and converted to SQLite databases.
    """)
    
    st.header("Upload Medical Data")
    st.info("To use the data analysis features, please upload your medical CSV files:")
    
    uploaded_heart = st.file_uploader("Heart Disease Data (CSV)", type="csv")
    uploaded_cancer = st.file_uploader("Cancer Data (CSV)", type="csv")
    uploaded_diabetes = st.file_uploader("Diabetes Data (CSV)", type="csv")
    
    if uploaded_heart:
        df = pd.read_csv(uploaded_heart)
        conn = sqlite3.connect("heart_disease.db")
        df.to_sql("heart_disease", conn, if_exists="replace", index=False)
        conn.close()
        st.success("Heart disease data uploaded successfully!")
    
    if uploaded_cancer:
        df = pd.read_csv(uploaded_cancer)
        conn = sqlite3.connect("cancer.db")
        df.to_sql("cancer", conn, if_exists="replace", index=False)
        conn.close()
        st.success("Cancer data uploaded successfully!")
    
    if uploaded_diabetes:
        df = pd.read_csv(uploaded_diabetes)
        conn = sqlite3.connect("diabetes.db")
        df.to_sql("diabetes", conn, if_exists="replace", index=False)
        conn.close()
        st.success("Diabetes data uploaded successfully!")
    
    st.header("Examples")
    if st.button("Heart disease data analysis"):
        st.session_state.messages.append({"role": "user", "content": "What is the average age of patients with heart disease?"})
    
    if st.button("Diabetes symptoms"):
        st.session_state.messages.append({"role": "user", "content": "What are the common symptoms of diabetes?"})
    
    if st.button("Cancer statistics"):
        st.session_state.messages.append({"role": "user", "content": "How many cases of each cancer type are in the dataset?"})

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask a medical question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.agent.ask_question(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
