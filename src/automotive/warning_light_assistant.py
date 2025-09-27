
import os

import openai
import streamlit as st

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.warning('Set the OPENAI_API_KEY environment variable to enable the warning light assistant.')

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

st.title('Car Dashboard Warning Light Assistant')

user_query = st.text_input("Describe the warning light or issue you're seeing:")

if st.button('Get Information'):
    if not user_query:
        st.warning('Please enter a description of the warning light or issue.')
    elif client is None:
        st.error('OpenAI key missing. Configure OPENAI_API_KEY to enable responses.')
    else:
        prompt = f"""You are an AI assistant specialising in car maintenance for Indian vehicles.
The driver reports the following dashboard light or issue:
{user_query}

Explain what the warning indicates, its severity, recommended actions, and safety precautions.
If a professional mechanic is required, mention it explicitly."""
        with st.spinner('Analyzing the warning light...'):
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': 'You are a helpful car maintenance assistant.'},
                    {'role': 'user', 'content': prompt},
                ],
                max_tokens=400,
                temperature=0.4,
            )
        st.subheader('Analysis Result:')
        st.write(response.choices[0].message.content.strip())

st.sidebar.warning('Always consult a certified mechanic if you are unsure about a warning light or hear abnormal sounds.')
