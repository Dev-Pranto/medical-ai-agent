# Medical AI Assistant with Gemini and Streamlit

A multi-tool AI agent that can answer questions about medical datasets and general medical knowledge using Google's Gemini model.

## Features

- Answers data-specific queries from three medical datasets:
  - Heart Disease Dataset
  - Cancer Prediction Dataset
  - Diabetes Dataset
- Uses web search for general medical knowledge (definitions, symptoms, treatments)
- Clean Streamlit web interface
- Powered by Google's Gemini AI model

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `TAVILY_API_KEY`: Your Tavily API key (optional, for web search)
4. Upload your medical datasets through the Streamlit interface

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your GitHub account and select this repository
4. Set the following secrets in Streamlit Cloud:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `TAVILY_API_KEY`: Your Tavily API key (optional)
5. Deploy the app

## Usage

1. Open the web application
2. Upload your medical CSV files through the sidebar
3. Ask questions in the chat interface such as:
   - "What is the average age of heart disease patients?"
   - "What are the symptoms of diabetes?"
   - "Show me statistics about cancer cases"
4. The AI will automatically determine whether to use the medical datasets or web search

## Project Structure

- `app.py`: Streamlit web application
- `medical_agent.py`: Core AI agent with Gemini integration
- `requirements.txt`: Python dependencies
