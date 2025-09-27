import os
import asyncio
import aiohttp
import streamlit as st
import pandas as pd
import openai
from PyPDF2 import PdfReader
from fpdf import FPDF

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Sidebar navigation for tabs
st.sidebar.header("Navigation")
tabs = [
    "Main Page",
    "Sentiment Analysis",
    "Topic Classification",
    "Urgency Classification",
    "Language Detection",
    "Aspect-based Sentiment Analysis",
    "Real-Time Feedback and Adaptation",
    "Automated Ticket Routing",
    "Daily Monitoring",
    "Monthly Report"
]
selected_tab = st.sidebar.radio("Select a tab:", tabs)

# Ensure session state for ticket_text and API responses
if 'ticket_text' not in st.session_state:
    st.session_state.ticket_text = ""

if 'responses' not in st.session_state:
    st.session_state.responses = {}

if 'daily_report_data' not in st.session_state:
    st.session_state.daily_report_data = None

if 'monthly_report_data' not in st.session_state:
    st.session_state.monthly_report_data = None

if 'daily_analysis' not in st.session_state:
    st.session_state.daily_analysis = None

if 'monthly_analysis' not in st.session_state:
    st.session_state.monthly_analysis = None

# Main Page Content
if selected_tab == "Main Page":
    st.title("🛠️ Ticket Analysis Dashboard 🛠️")
    st.write("""
    Welcome to the Ticket Analysis Dashboard! This tool allows you to analyze ticket data and extract insights to improve customer service. 
    Upload a CSV file containing ticket data or enter ticket details manually and explore various analytical insights including sentiment analysis, 
    topic classification, and more. Let's dive in! 📊
    """)

    st.header("Input Ticket Data")
    ticket_input_method = st.selectbox("Select Input Method", ["Text Input", "Text File", "PDF File"])

    if ticket_input_method == "Text Input":
        ticket_text = st.text_area("Enter Ticket Text")
        if st.button("Submit"):
            st.session_state.ticket_text = ticket_text
            st.success("Ticket text input received.")
    elif ticket_input_method == "Text File":
        uploaded_text_file = st.file_uploader("Choose a text file", type="txt")
        if uploaded_text_file is not None:
            ticket_text = uploaded_text_file.read().decode("utf-8")
            st.session_state.ticket_text = ticket_text
            st.success("Text file loaded successfully!")
    elif ticket_input_method == "PDF File":
        uploaded_pdf_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_pdf_file is not None:
            pdf_reader = PdfReader(uploaded_pdf_file)
            ticket_text = ""
            for page in pdf_reader.pages:
                ticket_text += page.extract_text()
            st.session_state.ticket_text = ticket_text
            st.success("PDF file loaded successfully!")

# File upload section for daily/monthly CSV reports
if selected_tab == "Daily Monitoring":
    st.sidebar.header("Upload CSV for Daily Monitoring Reports")
    uploaded_daily_csv_file = st.sidebar.file_uploader("Choose a Daily CSV file", type="csv")

    if uploaded_daily_csv_file is not None:
        st.session_state.daily_report_data = pd.read_csv(uploaded_daily_csv_file)
        st.sidebar.success("Daily CSV data loaded successfully!")

if selected_tab == "Monthly Report":
    st.sidebar.header("Upload CSV for Monthly Reports")
    uploaded_monthly_csv_file = st.sidebar.file_uploader("Choose a Monthly CSV file", type="csv")

    if uploaded_monthly_csv_file is not None:
        st.session_state.monthly_report_data = pd.read_csv(uploaded_monthly_csv_file)
        st.sidebar.success("Monthly CSV data loaded successfully!")

# Function to generate response from OpenAI
async def generate_response(session, prompt):
    try:
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": "You are an AI assistant providing detailed and accurate analysis for customer service tickets. Your role is to offer insights and recommendations based on ticket data patterns."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            },
            ssl=False
        ) as response:
            result = await response.json()
            if response.status == 200 and 'choices' in result:
                return result['choices'][0]['message']['content'].strip()
            else:
                st.error(f"Error: {result.get('error', {}).get('message', 'Unknown error')}")
                return "An error occurred or the response format is unexpected."
    except Exception as e:
        st.error(f"Exception: {e}")
        return "An error occurred while generating the response."

# Fetch all data before rendering
if st.session_state.ticket_text and not st.session_state.responses:
    ticket_text = st.session_state.ticket_text
    prompts = {
        "Sentiment Analysis": f"""
            Determine the sentiment of the ticket (positive, negative, neutral).
            Data: 
            {ticket_text[:500]}...  # Displaying only the first 500 characters
        """,
        "Topic Classification": f"""
            Identify the main topic or category of the ticket.
            Data: 
            {ticket_text[:500]}...
        """,
        "Urgency Classification": f"""
            Assess the urgency level of the ticket (high, medium, low).
            Data: 
            {ticket_text[:500]}...
        """,
        "Language Detection": f"""
            Detect the language of the ticket.
            Data: 
            {ticket_text[:500]}...
        """,
        "Aspect-based Sentiment Analysis": f"""
            Combine sentiment and topic analysis for deeper insights.
            Data: 
            {ticket_text[:500]}...
        """,
        "Real-Time Feedback and Adaptation": f"""
            Provide immediate response capabilities and suggest actions.
            Data: 
            {ticket_text[:500]}...
        """,
        "Automated Ticket Routing": f"""
            Automatically route tickets to the appropriate team or individual based on classification.
            Data: 
            {ticket_text[:500]}...
        """
    }

    # Asynchronous function to fetch responses from OpenAI
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = [generate_response(session, prompt) for prompt in prompts.values()]
            responses_list = await asyncio.gather(*tasks)
            st.session_state.responses = dict(zip(prompts.keys(), responses_list))

    # Run the asynchronous function and fetch responses
    asyncio.run(main())

# Asynchronous function to fetch responses from OpenAI for daily and monthly reports
async def fetch_report_analysis():
    async with aiohttp.ClientSession() as session:
        tasks = []

        if st.session_state.daily_report_data is not None:
            daily_data_sample = st.session_state.daily_report_data.head(5).to_string()
            daily_prompt = f"""
                Create a summary of the issues for the day, including most reported products/services, and the status of tickets (resolved/unresolved).
                Data: 
                {daily_data_sample}
            """
            tasks.append(generate_response(session, daily_prompt))

        if st.session_state.monthly_report_data is not None:
            monthly_data_sample = st.session_state.monthly_report_data.head(5).to_string()
            monthly_prompt = f"""
                Create a summary of the issues for the month, highlighting key insights.
                Data: 
                {monthly_data_sample}
            """
            tasks.append(generate_response(session, monthly_prompt))

        if tasks:
            responses = await asyncio.gather(*tasks)
            if len(responses) > 0:
                st.session_state.daily_analysis = responses[0] if len(responses) > 0 else None
                st.session_state.monthly_analysis = responses[1] if len(responses) > 1 else None

# Fetch daily and monthly analysis data if needed
if (selected_tab == "Daily Monitoring" and st.session_state.daily_report_data is not None) or \
   (selected_tab == "Monthly Report" and st.session_state.monthly_report_data is not None):
    asyncio.run(fetch_report_analysis())

# Function to create PDF
def create_pdf(title, content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.multi_cell(0, 10, content)
    return pdf

# Function to download the PDF file
def download_pdf(content, filename):
    pdf = create_pdf("Ticket Analysis Report", content)
    pdf_output = f"/Users/saylibande/Desktop/work/tickets/{filename}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Display content based on selected tab
if selected_tab in ["Sentiment Analysis", "Topic Classification", "Urgency Classification", "Language Detection", "Aspect-based Sentiment Analysis", "Real-Time Feedback and Adaptation", "Automated Ticket Routing"]:
    st.header(selected_tab)
    analysis_content = st.session_state.responses.get(selected_tab, "Loading...")
    st.write(analysis_content)

elif selected_tab == "Daily Monitoring":
    st.header("Daily Monitoring Analysis")
    if st.session_state.daily_report_data is not None:
        st.write(st.session_state.daily_report_data.head())  # Display the first few rows of the data as a preview
        st.write("Summary Analysis:")
        daily_analysis_content = st.session_state.daily_analysis or "Analyzing data, please wait..."
        st.write(daily_analysis_content)
        if st.button("Download Daily Report as PDF"):
            daily_pdf_path = download_pdf(daily_analysis_content, "Daily_Report")
            st.write(f"Download your report [here]({daily_pdf_path})")
    else:
        st.write("Please upload a Daily CSV file to get started.")

elif selected_tab == "Monthly Report":
    st.header("Monthly Report Analysis")
    if st.session_state.monthly_report_data is not None:
        st.write(st.session_state.monthly_report_data.head())  # Display the first few rows of the data as a preview
        st.write("Summary Analysis:")
        monthly_analysis_content = st.session_state.monthly_analysis or "Analyzing data, please wait..."
        st.write(monthly_analysis_content)
        if st.button("Download Monthly Report as PDF"):
            monthly_pdf_path = download_pdf(monthly_analysis_content, "Monthly_Report")
            st.write(f"Download your report [here]({monthly_pdf_path})")
    else:
        st.write("Please upload a Monthly CSV file to get started.")
