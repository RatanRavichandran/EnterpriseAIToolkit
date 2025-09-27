from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

import openai
import pandas as pd
import requests
import streamlit as st
from bs4 import BeautifulSoup

openai.api_key = os.getenv('OPENAI_API_KEY')
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
    )
}
REPO_ROOT = Path(__file__).resolve().parents[4]
DEFAULT_PROFILE_PATH = REPO_ROOT / 'data' / 'reference' / 'sample_user_profile.txt'


def _fetch_product_page(url: str) -> BeautifulSoup:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')


def _extract_text(soup: BeautifulSoup, selector: str, *, attr: str | None = None) -> str:
    element = soup.select_one(selector)
    if not element:
        return ''
    if attr:
        return element.get(attr, '').strip()
    return element.get_text(strip=True)


def _extract_product_details(product_url: str) -> Dict[str, str]:
    soup = _fetch_product_page(product_url)

    asin = _extract_text(
        soup,
        "#detailBullets_feature_div li:has(span:contains('ASIN')) span.a-list-item > span:last-child",
    )
    manufacturer = _extract_text(
        soup,
        "#detailBullets_feature_div li:has(span:contains('Manufacturer')) span.a-list-item > span:last-child",
    )

    description = _extract_text(soup, "div#feature-bullets")
    if not description:
        description = _extract_text(soup, "div#productDescription")

    return {
        'Product Name': _extract_text(soup, "span#productTitle"),
        'Product URL': product_url,
        'Product Price': _extract_text(soup, "span.a-price-whole"),
        'Product Rating': _extract_text(soup, "span.a-icon-alt"),
        'Number of Reviews': _extract_text(soup, "span#acrCustomerReviewText").split(' ')[0],
        'ASIN': asin,
        'Manufacturer': manufacturer,
        'Description': description,
        'Product Description': description,
    }


def _call_openai(prompt: str, *, max_tokens: int = 300) -> str:
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured.')

    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'You are a helpful e-commerce analyst.'},
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()


def summarize_description(description: str) -> str:
    prompt = f"Summarise the following product description for a consumer: {description}"
    return _call_openai(prompt, max_tokens=200)


def read_user_profile(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f'User profile file not found at {path}. Update the path or upload a profile file.'
        )
    return path.read_text(encoding='utf-8').strip()


def generate_personalised_recommendation(user_profile: str, product_summary: str) -> str:
    prompt = (
        'User Profile:\n'
        f'{user_profile}\n\n'
        'Product Summary:\n'
        f'{product_summary}\n\n'
        'Strictly use the profile context to answer whether the user will like the product. '
        'Highlight reasons to buy and possible objections from the profile point of view.'
    )
    return _call_openai(prompt, max_tokens=700)


st.set_page_config(page_title='Product Summary & Fit Assessment')
st.title('Amazon Product Analyzer and Profile Fit')

product_url = st.text_input('Enter the product URL:')
profile_path_input = st.text_input(
    'Path to user profile text file (optional)',
    value=str(DEFAULT_PROFILE_PATH),
)

if st.button('Get Product Details and Recommendations'):
    if not product_url:
        st.error('Please enter a valid product URL.')
    else:
        try:
            details = _extract_product_details(product_url)
        except Exception as exc:  # pylint: disable=broad-except
            st.error(f'Failed to fetch product details: {exc}')
        else:
            df = pd.DataFrame([details])
            st.subheader('Product Details')
            st.dataframe(df, use_container_width=True)

            description = details.get('Product Description', '')
            if description:
                summary = summarize_description(description)
                st.subheader('Product Summary')
                st.write(summary)
            else:
                summary = ''
                st.info('No description found to summarise.')

            if summary:
                try:
                    profile_text = read_user_profile(Path(profile_path_input))
                except FileNotFoundError as err:
                    st.warning(str(err))
                else:
                    recommendation = generate_personalised_recommendation(profile_text, summary)
                    st.subheader('Personalised Recommendation Fit')
                    st.write(recommendation)
