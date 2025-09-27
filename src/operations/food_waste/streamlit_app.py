import streamlit as st
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import openai
from io import BytesIO
import os
from dotenv import load_dotenv
import csv
from io import StringIO
import pandas as pd
import mimetypes
import plotly.express as px


load_dotenv()

# Get the API key from environment variables
openai.api_key = os.getenv('OPENAI_API_KEY')

st.set_page_config(page_title="BuckStars Food Wastage Data Analyzer")

def process_pdfs(pdf_files):
    raw_text = ''
    for pdf_file in pdf_files:
        pdf_bytes = pdf_file.getvalue()
        pdf_io = BytesIO(pdf_bytes)
        pdfreader = PdfReader(pdf_io)
        for page in pdfreader.pages:
            content = page.extract_text()
            if content:
                raw_text += content
    return raw_text

def process_csv(csv_files):
    raw_data = []
    for csv_file in csv_files:
        csv_bytes = csv_file.getvalue()
        csv_io = StringIO(csv_bytes.decode('utf-8'))
        df = pd.read_csv(csv_io)
        raw_data.append(df)
    return raw_data

def process_excel(excel_files):
    raw_data = []
    for excel_file in excel_files:
        excel_bytes = excel_file.getvalue()
        excel_io = BytesIO(excel_bytes)
        df = pd.read_excel(excel_io)
        raw_data.append(df)
    return raw_data

def load_additional_data(data_dir):
    additional_texts = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".pdf"):
            with open(os.path.join(data_dir, filename), "rb") as f:
                pdfreader = PdfReader(f)
                raw_text = ''
                for page in pdfreader.pages:
                    content = page.extract_text()
                    if content:
                        raw_text += content
                additional_texts.append(raw_text)
    return additional_texts

def create_vectorstore(texts):
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(texts)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index, embeddings, model

def find_context(query, index, embeddings, model, texts, top_k=5):
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)
    relevant_texts = [texts[i] for i in indices[0]]
    return " ".join(relevant_texts)

def analyze_data(prompt, context):
    messages = [{"role": "system", "content": """
As an expert in food wastage analysis and reduction, your role is to provide detailed, actionable insights and recommendations based on the data provided. The data may include information on waste quantities, spoilage rates, inventory levels, and various operational metrics related to food wastage.

Your analysis should cover the following aspects in detail:

1. Waste Analysis:
    - Waste Trends: Identify and explain patterns in food waste over time, including peak periods and declining phases. Use actual waste data to highlight specific trends (e.g., "Waste of fresh produce increased by 25% during the last quarter").
    - Spoilage Trends: Examine spoilage rates over time, noting any significant fluctuations or patterns. Provide examples from the data (e.g., "Spoilage of dairy products peaked during the summer months").

2. Operational Efficiency:
    - Process Optimization: Identify inefficiencies in processes contributing to food waste. Use specific data points to support recommendations (e.g., "High spoilage rates in prepared meals suggest a need for better inventory management or revised preparation protocols").
    - Inventory Management: Analyze inventory data to recommend optimal stock levels and rotation practices. Provide examples (e.g., "Increased spoilage in vegetables could be mitigated by implementing a first-in, first-out inventory system").

3. Waste Reduction Strategies:
    - Reduction Techniques: Suggest strategies for reducing food waste based on data trends. Use examples to illustrate potential impact (e.g., "Reducing portion sizes by 10% could lower waste by 15%").
    - Spoilage Control: Recommend methods to manage spoilage, supported by data analysis (e.g., "Regular temperature checks and proper storage could reduce spoilage rates by 20%").

4. Cost Management:
    - Cost-Saving Measures: Advise on measures to reduce costs associated with food waste, using data to highlight potential savings (e.g., "Implementing waste tracking systems could save $10,000 annually on wasted inventory").
    - Resource Allocation: Recommend optimal resource allocation to minimize waste, based on data analysis (e.g., "Allocating more resources to high-turnover items could improve profitability and reduce waste").

Ensure your responses are actionable, relevant, and tailored to the food industry. Use actual examples from the provided data to give weight to your analysis and recommendations.

    """}]
    
    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})
    
    messages.append({"role": "user", "content": prompt})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

def display_chat_history(chat_history):
    for message in chat_history:
        st.write(message)  # Adjust formatting as needed

def handle_user_query(query, context=None):
    # Simplified prompt for free-form analysis
    messages = [
        {"role": "system", "content": """
        As an AI, your task is to analyze the user's query concerning food wastage and reduction based on the data provided. Ensure that your insights and recommendations are specific to food wastage and relevant to the food industry. 

        Your response should address the following:

        1. Data-Driven Insights: Provide specific, data-backed insights related to food waste and spoilage. Use data examples to explain patterns or anomalies (e.g., "Spoilage rates increased by 10% in the summer months").

        2. Recommendations: Offer practical recommendations to reduce food waste and manage spoilage. Use examples to support suggestions (e.g., "Implementing waste tracking systems could reduce overall waste by 15%").

        3. Contextual Relevance: Ensure the insights are relevant to food wastage and tailored to the specific context of the query. Provide actionable steps (e.g., "Adjust inventory levels to reduce overstocking and waste").

        4. Actionability: Provide clear, feasible steps based on your analysis. These should be specific and actionable (e.g., "Revise menu offerings based on waste data to minimize excess").

        Always validate your response with actual data examples to enhance the credibility and applicability of your advice.
        """}
    ]
    
    if context:
        messages.append({"role": "system", "content": f"Context: {context}"})
    
    messages.append({"role": "user", "content": query})
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    return response.choices[0].message['content'].strip()

import streamlit as st
import mimetypes
from io import BytesIO, StringIO
import pandas as pd
from PyPDF2 import PdfReader

# Assuming other necessary imports and functions are already defined as in the initial script

import streamlit as st
import mimetypes
from io import BytesIO, StringIO
import pandas as pd
from PyPDF2 import PdfReader

# Assuming other necessary imports and functions are already defined as in the initial script

def main():
    st.title("BuckStars Food Wastage Data Analyzer")
    
    # Initialize chat history in session state if not already present
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=["pdf", "csv", "xlsx", "xls"])
    if uploaded_files:
        if 'raw_data' not in st.session_state or 'context' not in st.session_state:
            st.session_state.raw_data = []
            for uploaded_file in uploaded_files:
                mime_type = mimetypes.guess_type(uploaded_file.name)[0]
                if mime_type == "application/pdf":
                    raw_text = process_pdfs([uploaded_file])
                    st.session_state.raw_data.append(raw_text)
                elif mime_type.startswith("text/csv"):
                    raw_csv = process_csv([uploaded_file])
                    st.session_state.raw_data.extend([" ".join(map(str, row)) for row in raw_csv[0].values.tolist()])
                elif mime_type.startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") or \
                     mime_type.startswith("application/vnd.ms-excel"):
                    raw_excel = process_excel([uploaded_file])
                    st.session_state.raw_data.extend([" ".join(map(str, row)) for row in raw_excel[0].values.tolist()])
            
            st.write("Files processed successfully!")
            
            if st.session_state.raw_data:
                index, embeddings, model = create_vectorstore(st.session_state.raw_data)
                prompt = "Analyze the provided data and offer actionable insights for reducing food wastage in a food and beverage company."
                st.session_state.context = find_context(prompt, index, embeddings, model, st.session_state.raw_data)
                st.session_state.initial_analysis = analyze_data(prompt, st.session_state.context)
        
        with st.container():
            st.header("Food Wastage Analysis")
            st.write(st.session_state.initial_analysis)
        
        with st.container():
            st.header("Ask Further Questions")
            with st.form("Query Form"):
                user_message = st.text_input("Type your question here:", key="user_question")
                submit_button = st.form_submit_button("Send")
                if submit_button and user_message:
                    if 'context' in st.session_state:
                        response_content = handle_user_query(user_message, st.session_state.context)
                        # Update chat history
                        st.session_state.chat_history.append({"user": user_message, "response": response_content})
                    else:
                        response_content = "Context is not available. Please upload files and generate context first."
                    st.write(response_content)

    # Display chat history
    if st.session_state.chat_history:
        st.write("### Chat History")
        for chat in st.session_state.chat_history:
            st.write(f"**Question:** {chat['user']}")
            st.write(f"**Answer:** {chat['response']}")
            st.write("---")  # Adds a horizontal line for better separation

if __name__ == "__main__":
    main()

