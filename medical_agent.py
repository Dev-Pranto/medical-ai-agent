import google.generativeai as genai
import sqlite3
import pandas as pd
from tavily import TavilyClient
import re

class MedicalAIAgent:
    def __init__(self, gemini_api_key, tavily_api_key=None):
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Configure Tavily for web search (optional)
        self.tavily_client = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None
        
        # Database paths
        self.db_paths = {
            "heart": "databases/heart_disease.db",
            "cancer": "databases/cancer.db",
            "diabetes": "databases/diabetes.db"
        }
    
    def query_database(self, db_name, query):
        """Execute SQL query on the specified database"""
        try:
            conn = sqlite3.connect(self.db_paths[db_name])
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            return f"Error querying database: {str(e)}"
    
    def get_table_schema(self, db_name):
        """Get schema information for a database"""
        try:
            conn = sqlite3.connect(self.db_paths[db_name])
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            schema_info = f"Database: {db_name}\n"
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                schema_info += f"Table: {table_name}\n"
                for col in columns:
                    schema_info += f"  {col[1]} ({col[2]})\n"
            
            conn.close()
            return schema_info
        except Exception as e:
            return f"Error getting schema: {str(e)}"
    
    def web_search(self, query):
        """Perform a web search using Tavily"""
        if not self.tavily_client:
            return "Web search is not configured. Please provide a Tavily API key."
        
        try:
            response = self.tavily_client.search(query, max_results=3)
            return "\n\n".join([f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}" 
                               for r in response['results']])
        except Exception as e:
            return f"Error performing web search: {str(e)}"
    
    def generate_sql_query(self, question, db_name):
        """Use Gemini to generate an SQL query from a natural language question"""
        schema = self.get_table_schema(db_name)
        
        prompt = f"""
        You are a medical data analyst. Based on the database schema below, generate an SQL query to answer the question.
        Only respond with the SQL query, nothing else.
        
        Database Schema:
        {schema}
        
        Question: {question}
        
        SQL Query:
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract SQL query from response (Gemini might add backticks)
            sql_query = response.text.strip()
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            return sql_query.strip()
        except Exception as e:
            return f"Error generating SQL query: {str(e)}"
    
    def ask_question(self, question):
        """Route the question to the appropriate tool and get an answer"""
        question_lower = question.lower()
        
        # Determine which database to use (if any)
        db_to_use = None
        if any(word in question_lower for word in ["heart", "cardiac", "cholesterol", "blood pressure"]):
            db_to_use = "heart"
        elif any(word in question_lower for word in ["cancer", "tumor", "malignant", "benign"]):
            db_to_use = "cancer"
        elif any(word in question_lower for word in ["diabetes", "glucose", "insulin"]):
            db_to_use = "diabetes"
        
        # Check if it's a data query vs general knowledge
        data_keywords = ["data", "statistic", "analysis", "dataset", "record", "patient", "cases", "average", "count", "sum"]
        has_data_keyword = any(keyword in question_lower for keyword in data_keywords)
        
        if db_to_use and has_data_keyword:
            # This is a data query - use the database
            sql_query = self.generate_sql_query(question, db_to_use)
            if sql_query.startswith("Error"):
                return sql_query
            
            result = self.query_database(db_to_use, sql_query)
            
            if isinstance(result, str) and result.startswith("Error"):
                return result
            
            # Use Gemini to interpret the results
            prompt = f"""
            Based on the following SQL query results, answer the question in a helpful way.
            If the results are empty, explain what that might mean.
            
            Question: {question}
            SQL Query: {sql_query}
            Results:
            {result.to_string() if hasattr(result, 'to_string') else result}
            
            Please provide a concise answer:
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error interpreting results: {str(e)}"
        
        else:
            # This is a general knowledge question - use web search
            search_results = self.web_search(question)
            
            # Use Gemini to synthesize the search results
            prompt = f"""
            Based on the following web search results, answer the question in a helpful way.
            Cite sources when appropriate.
            
            Question: {question}
            Search Results:
            {search_results}
            
            Please provide a comprehensive answer:
            """
            
            try:
                response = self.model.generate_content(prompt)
                return response.text
            except Exception as e:
                return f"Error synthesizing search results: {str(e)}"
