
from __future__ import annotations

import os
from typing import List

import streamlit as st
from langchain_openai import ChatOpenAI

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    st.warning('Set the OPENAI_API_KEY environment variable to enable AI-backed recommendations.')

llm = ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo', openai_api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

QUESTIONS: List[str] = [
    'What is your budget range for a car (in lakhs)?',
    'Do you prefer a compact, mid-size, or large car?',
    'What fuel type do you prefer (petrol, diesel, electric, hybrid)?',
    'Is fuel efficiency a top priority for you?',
    'Do you need a car primarily for city driving or long trips?',
    'How important is boot space to you?',
    'Do you prefer automatic or manual transmission?',
    'Are you looking for any specific safety features?',
    'How important is brand reputation to you?',
    'Are you interested in any particular advanced technologies (e.g., infotainment system, driver assistance)?',
]

SYSTEM_PROMPT = (
    'As an AI, you will provide car recommendations for Indian buyers based on their preferences.
'
    'Summarise the preferences, suggest 3-5 relevant models available in India with justification, '
    'and close with additional considerations the buyer should evaluate.'
)


def collect_preferences() -> List[str]:
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = [SYSTEM_PROMPT]
    st.write("Bot: Hello, let's find the perfect car for you with a quick questionnaire.")
    for question in QUESTIONS:
        st.write(f"Bot: {question}")
        answer = st.text_input('You:', key=question)
        if answer:
            st.session_state.conversation_history.append(f"Bot: {question}")
            st.session_state.conversation_history.append(f"You: {answer}")
    return st.session_state.conversation_history


def create_recommendations(history: List[str]) -> str:
    if llm is None:
        return 'Model not configured. Set the OPENAI_API_KEY to enable recommendations.'
    response = llm.invoke(history)
    return response.content


def compare_recommendations(resp_past: str, resp_present: str) -> str:
    if llm is None:
        return 'Model not configured. Set the OPENAI_API_KEY to compare recommendations.'
    prompt = (
        'Compare the following car recommendation reports highlighting what changed and why.
'
        f'Past recommendations: {resp_past}
'
        f'Latest recommendations: {resp_present}'
    )
    return llm.invoke(prompt).content


def main() -> None:
    st.title('Car Recommendation Bot for Indian Buyers')

    if 'resp_past' not in st.session_state:
        st.session_state.resp_past = ''
    if 'resp_present' not in st.session_state:
        st.session_state.resp_present = ''

    history = collect_preferences()

    if st.button('Get Car Recommendations'):
        recommendations = create_recommendations(history)
        st.session_state.resp_present = recommendations
        st.subheader('Car Recommendations')
        st.text_area('Recommendations', value=recommendations, height=300)

    if st.session_state.resp_past and st.session_state.resp_present:
        comparison = compare_recommendations(st.session_state.resp_past, st.session_state.resp_present)
        st.subheader('Preference Shift Comparison')
        st.text_area('Preference Comparison', value=comparison, height=300)

    if st.button('Start a new recommendation?'):
        st.session_state.resp_past = st.session_state.resp_present
        st.session_state.resp_present = ''
        st.experimental_rerun()


if __name__ == '__main__':
    main()
