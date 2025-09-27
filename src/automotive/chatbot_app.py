
import os
from typing import List

import openai
import streamlit as st

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.warning('Set the OPENAI_API_KEY environment variable to enable the automotive assistant.')

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = """You are an expert automotive advisor specialising in Indian cars and accessories.
Provide detailed, accurate answers grounded in the Indian market context. Highlight legal/safety considerations when relevant."""

st.title('Automotive Advisor Chatbot')

if 'messages' not in st.session_state:
    st.session_state.messages = [{'role': 'system', 'content': SYSTEM_PROMPT}]

for message in st.session_state.messages[1:]:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt := st.chat_input('Ask about cars, accessories, maintenance, or regulations in India'):
    st.chat_message('user').markdown(prompt)
    st.session_state.messages.append({'role': 'user', 'content': prompt})

    if client is None:
        response_text = 'OpenAI key missing. Configure OPENAI_API_KEY to enable the assistant.'
    else:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=st.session_state.messages,
            max_tokens=600,
            temperature=0.7,
        )
        response_text = response.choices[0].message.content.strip()

    with st.chat_message('assistant'):
        st.markdown(response_text)
    st.session_state.messages.append({'role': 'assistant', 'content': response_text})

st.sidebar.title('About')
st.sidebar.info('Demo assistant showcasing automotive expertise for the Indian market using OpenAI chat models.')
