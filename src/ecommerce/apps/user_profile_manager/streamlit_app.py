from __future__ import annotations

import os
import random
import sqlite3
from pathlib import Path
from typing import Dict, Tuple

import openai
import streamlit as st
from faker import Faker

openai.api_key = os.getenv('OPENAI_API_KEY')
REPO_ROOT = Path(__file__).resolve().parents[4]
DB_PATH = REPO_ROOT / 'data' / 'reference' / 'ecommerce.db'
CATEGORIES = ['Electronics', 'Clothing', 'Home Appliances', 'Books', 'Toys', 'Groceries', 'Beauty']


@st.cache_resource(show_spinner=False)
def _get_connection(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise FileNotFoundError(f'Database not found at {db_path}. Ensure the demo DB is available.')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _call_openai(prompt: str, *, max_tokens: int = 800) -> str:
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured.')

    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'You are an AI consultant for e-commerce platforms.'},
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def insert_or_update_user_profile(conn: sqlite3.Connection, user_id: str, new_data: Dict[str, object]) -> None:
    placeholders = (
        user_id,
        new_data['age'],
        new_data['gender'],
        new_data['marital_status'],
        new_data['income_level'],
        new_data['education'],
        new_data['occupation'],
        new_data['residential_status'],
        new_data['dependents'],
        new_data['average_spending'],
        ', '.join(new_data['preferred_categories']),
        ', '.join(new_data['browsing_history']),
    )

    with conn:
        conn.execute(
            '''
            INSERT INTO user_profiles (
                user_id, age, gender, marital_status, income_level, education,
                occupation, residential_status, dependents, average_spending,
                preferred_categories, browsing_history
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                age=excluded.age,
                gender=excluded.gender,
                marital_status=excluded.marital_status,
                income_level=excluded.income_level,
                education=excluded.education,
                occupation=excluded.occupation,
                residential_status=excluded.residential_status,
                dependents=excluded.dependents,
                average_spending=excluded.average_spending,
                preferred_categories=excluded.preferred_categories,
                browsing_history=excluded.browsing_history
            ''',
            placeholders,
        )


def fetch_user_profile(conn: sqlite3.Connection, user_id: str) -> Tuple[str, ...] | None:
    cursor = conn.execute('SELECT * FROM user_profiles WHERE user_id = ?', (user_id,))
    return cursor.fetchone()


def generate_recommendations(user_profile: Tuple[str, ...]) -> str:
    prompt = (
        'Generate product recommendations for the following e-commerce customer profile. '
        'Return personalised, actionable suggestions in a friendly tone.\n'
        f'{dict(user_profile)}'
    )
    return _call_openai(prompt)


def save_user_profile_to_text(row: sqlite3.Row) -> Path:
    output_path = Path(f'user_profile_{row["user_id"]}.txt')
    with output_path.open('w', encoding='utf-8') as handle:
        for key in row.keys():
            handle.write(f'{key}: {row[key]}\n')
    return output_path


st.set_page_config(page_title='Customer Profile Studio')
st.title('E-commerce Customer Profile Studio')

try:
    connection = _get_connection(DB_PATH)
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

if not openai.api_key:
    st.warning('Set the OPENAI_API_KEY environment variable to enable AI-powered features.')

faker = Faker()

st.sidebar.header('Generate New User Profile')
if st.sidebar.button('Generate Random Profile'):
    new_user_id = faker.uuid4()
    profile_data = {
        'age': random.randint(20, 70),
        'gender': random.choice(['Male', 'Female', 'Non-binary']),
        'marital_status': random.choice(['Single', 'Married', 'Divorced', 'Widowed']),
        'income_level': random.choice(['Low', 'Medium', 'High']),
        'education': random.choice(['High School', 'College', 'University']),
        'occupation': faker.job(),
        'residential_status': random.choice(['Owns house', 'Rents', 'Living with parents']),
        'dependents': random.randint(0, 5),
        'average_spending': round(random.uniform(100, 2000), 2),
        'preferred_categories': random.sample(CATEGORIES, 3),
        'browsing_history': random.sample(CATEGORIES, 5),
    }
    insert_or_update_user_profile(connection, new_user_id, profile_data)
    st.sidebar.success(f'Profile {new_user_id} stored successfully.')

st.sidebar.header('Manage Existing Profile')
user_id_input = st.sidebar.text_input('Enter User ID:')

def _render_profile(row: sqlite3.Row) -> None:
    st.subheader('Profile Snapshot')
    st.write({key: row[key] for key in row.keys()})

    if st.button('Get AI Recommendations'):
        st.write(generate_recommendations(tuple(row)))

    if st.button('Export Profile as Text'):
        saved_path = save_user_profile_to_text(row)
        st.success(f'Profile exported to {saved_path}')
        st.download_button(
            'Download profile text file',
            data=saved_path.read_text(encoding='utf-8'),
            file_name=saved_path.name,
        )

if st.sidebar.button('Load Profile'):
    if not user_id_input:
        st.sidebar.error('Please provide a user ID.')
    else:
        profile = fetch_user_profile(connection, user_id_input)
        if not profile:
            st.sidebar.error('User profile not found.')
        else:
            _render_profile(profile)
