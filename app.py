import streamlit as st
from medical_agent import MedicalAIAgent
import os

# Configure page
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide"
)

# Initialize session state
if "agent" not in st.session_state:
    # Get API keys from Streamlit secrets
    try:
        gemini_api_key = st.secrets["GEMINI_API_KEY"]
        tavily_api_key = st.secrets["TAVILY_API_KEY"]
    except:
        st.error("API keys not found. Please check your Streamlit secrets configuration.")
        st.stop()
    
    st.session_state.agent = MedicalAIAgent(gemini_api_key, tavily_api_key)

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
    
    **Datasets used:**
    - Heart Disease Dataset
    - Cancer Prediction Dataset
    - Diabetes Dataset
    """)
    
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
