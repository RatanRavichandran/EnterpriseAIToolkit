import os
import asyncio
import aiohttp
import streamlit as st
import pandas as pd
import openai
from fpdf import FPDF
from io import BytesIO
# Add these imports
from fpdf import FPDF
import tempfile
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Main page description with emojis
st.title("🚗 User-Centric Car Feature Analysis Dashboard 🚗")
st.write("""
Welcome to the User-Centric Car Feature Analysis Dashboard! This tool allows you to analyze user data and extract insights to enhance the driving experience. Upload a CSV file containing user data and explore various analytical insights including personalized settings, predictive maintenance, and more. Let's dive in! 🌟
""")

# File upload section with enhanced experience
st.sidebar.header("Upload User Data CSV")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the uploaded CSV file
    user_data = pd.read_csv(uploaded_file)
    st.sidebar.success("Data loaded successfully!")
else:
    st.sidebar.info("Please upload a CSV file to get started.")
    user_data = None

# Ensure session state for API responses
if 'responses' not in st.session_state:
    st.session_state.responses = {}

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
                    {"role": "system", "content": "You are an AI assistant providing detailed and accurate analysis for automotive data. Your role is to offer insights and recommendations based on user data patterns."},
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
if user_data is not None and not st.session_state.responses:
    prompts = {
        "Personalized Settings and Recommendations": f"""
            Based on the user's daily patterns over 10 days, identify trends in their driving behavior, infotainment usage, and climate control preferences. Suggest personalized settings for ADAS features, infotainment customization, and climate control adjustments to enhance their driving experience.
            Data: 
            {user_data.head(5).to_string()}
        """,
        "Predictive Maintenance": f"""
            Analyze the diagnostic alerts and response history for the user. Identify any recurring issues and predict potential future maintenance needs. Suggest a proactive maintenance schedule to prevent issues and ensure vehicle safety.
            Data: 
            {user_data.head(5).to_string()}
        """,
        "Enhanced User Interaction": f"""
            Examine the usage data for voice commands, including the frequency and types of commands issued, as well as the success rate. Provide recommendations to improve voice command recognition and response, ensuring a more seamless user experience.
            Data: 
            {user_data.head(5).to_string()}
        """,
        "Journey Suggestions": f"""
            Using data on common routes and peak usage times, suggest personalized journey options. This includes alternative routes, scenic paths, and real-time traffic updates tailored to their preferences and schedule.
            Data: 
            {user_data.head(5).to_string()}
        """,
        "User Profile Creation": f"""
            Create a comprehensive user profile based on the data collected from the user's interactions with the vehicle. This profile should include:
            1. Driving habits: Speed preferences, braking, and acceleration patterns.
            2. Infotainment preferences: Preferred music genres, radio stations, and screen interactions.
            3. Climate control settings: Temperature preferences and seat settings.

            Additionally, summarize the recommended solutions for each aspect to enhance user engagement and satisfaction.
            Data: 
            {user_data.head(5).to_string()}
        """,
        "Real-Time Feedback and Adaptation": f"""
            Develop a system for collecting and analyzing real-time feedback from the user, adapting the vehicle's features and services to better meet their needs. This includes tracking feedback on specific features and overall satisfaction, and integrating these insights into the vehicle's systems.
            Data: 
            {user_data.head(5).to_string()}
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

# Sidebar navigation for tabs
st.sidebar.header("Navigation")
tabs = [
    "Main Page",
    "Personalized Settings and Recommendations",
    "Predictive Maintenance",
    "Enhanced User Interaction",
    "Journey Suggestions",
    "User Profile Creation",
    "Real-Time Feedback and Adaptation"
]
selected_tab = st.sidebar.radio("Select a tab:", tabs)

# Function to create PDF
# Add this function
def create_pdf(user_profile, analytics):
    pdf = FPDF()
    pdf.add_page()
    
    # Set font
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "User-Centric Car Feature Analysis Report", 0, 1, "C")
    pdf.ln(10)
    
    # User Profile
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "User Profile", 0, 1)
    pdf.set_font("Arial", "", 12)
    for key, value in user_profile.items():
        pdf.cell(0, 10, f"{key}: {value}", 0, 1)
    pdf.ln(10)
    
    # Analytics
    for title, content in analytics.items():
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, 0, 1)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, content)
        pdf.ln(10)
    
    return pdf

# Display content based on selected tab
if selected_tab == "Main Page":
    if user_data is not None:
        st.header("User Data Overview")
        st.dataframe(user_data.head(10))  # Display first 10 rows of user data
    else:
        st.write("Please upload a CSV file to start analyzing.")

elif selected_tab == "Personalized Settings and Recommendations":
    st.header("Personalized Settings and Recommendations")
    st.write(st.session_state.responses.get("Personalized Settings and Recommendations", "Loading..."))

elif selected_tab == "Predictive Maintenance":
    st.header("Predictive Maintenance")
    st.write(st.session_state.responses.get("Predictive Maintenance", "Loading..."))

elif selected_tab == "Enhanced User Interaction":
    st.header("Enhanced User Interaction")
    st.write(st.session_state.responses.get("Enhanced User Interaction", "Loading..."))

elif selected_tab == "Journey Suggestions":
    st.header("Journey Suggestions")
    st.write(st.session_state.responses.get("Journey Suggestions", "Loading..."))

elif selected_tab == "User Profile Creation":
    st.header("User Profile Creation")
    if "User Profile Creation" in st.session_state.responses:
        user_profile_data = user_data.iloc[0]  # Get the first user's data for profile
        user_profile = {
            "User ID": user_profile_data['UserID'],
            "Driving Experience": f"{user_profile_data['Driving Experience']} years",
            "Preferred Routes": user_profile_data['Common Routes'],
            "Peak Usage Times": user_profile_data['Peak Usage Times'],
            "Preferred Music Genre": user_profile_data['Preferred Music Genre'],
            "Radio Station Preferences": user_profile_data['Radio Station Preferences'],
            "Climate Control Settings": f"{user_profile_data['Temperature Settings']} °C",
            "Fan Speed": user_profile_data['Fan Speed'],
            "Seat Heating/Cooling Usage": "Yes" if user_profile_data['Seat Heating/Cooling Usage'] else "No",
            "Voice Command Frequency": f"{user_profile_data['Voice Command Frequency']} commands/day",
            "Common Voice Commands": user_profile_data['Common Voice Commands'],
            "User Feedback": user_profile_data['User Feedback'],
            "NPS": user_profile_data['NPS']
        }

        st.subheader("👤 User Profile")
        with st.container():
            for key, value in user_profile.items():
                st.write(f"**{key}**: {value}")
        
        st.write(st.session_state.responses["User Profile Creation"])

elif selected_tab == "Real-Time Feedback and Adaptation":
    st.header("Real-Time Feedback and Adaptation")
    st.write(st.session_state.responses.get("Real-Time Feedback and Adaptation", "Loading..."))

# Download report
# Download report
st.sidebar.header("Download Report")
if st.sidebar.button("Download PDF Report"):
    if user_data is not None and st.session_state.responses:
        user_profile_data = user_data.iloc[0]  # Get the first user's data for profile
        user_profile = {
            "User ID": user_profile_data['UserID'],
            "Driving Experience": f"{user_profile_data['Driving Experience']} years",
            "Preferred Routes": user_profile_data['Common Routes'],
            "Peak Usage Times": user_profile_data['Peak Usage Times'],
            "Preferred Music Genre": user_profile_data['Preferred Music Genre'],
            "Radio Station Preferences": user_profile_data['Radio Station Preferences'],
            "Climate Control Settings": f"{user_profile_data['Temperature Settings']} °C",
            "Fan Speed": user_profile_data['Fan Speed'],
            "Seat Heating/Cooling Usage": "Yes" if user_profile_data['Seat Heating/Cooling Usage'] else "No",
            "Voice Command Frequency": f"{user_profile_data['Voice Command Frequency']} commands/day",
            "Common Voice Commands": user_profile_data['Common Voice Commands'],
            "User Feedback": user_profile_data['User Feedback'],
            "NPS": user_profile_data['NPS']
        }

        analytics = {tab: st.session_state.responses.get(tab, "No data available.") for tab in tabs[1:]}

        pdf = create_pdf(user_profile, analytics)
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
            pdf.output(tmpfile.name)
        
        # Read the temporary file into a BytesIO object
        with open(tmpfile.name, "rb") as f:
            pdf_data = f.read()
        
        # Delete the temporary file
        os.unlink(tmpfile.name)
        
        # Offer PDF for download
        st.sidebar.download_button(
            label="Click here to download PDF",
            data=pdf_data,
            file_name="car_feature_analysis_report.pdf",
            mime="application/pdf"
        )
    else:
        st.sidebar.warning("Please upload data and generate analysis before downloading the report.")
