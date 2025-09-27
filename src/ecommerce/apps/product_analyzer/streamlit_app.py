from __future__ import annotations

import os
from typing import Dict, List
from urllib.parse import urlparse

import openai
import streamlit as st
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from textblob import TextBlob

openai.api_key = os.getenv('OPENAI_API_KEY')


def _create_driver() -> webdriver.Chrome:
    """Create a headless Chrome driver, allowing an optional explicit binary path."""
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver_path = os.getenv('CHROMEDRIVER_PATH')
    service = Service(driver_path) if driver_path else Service()
    return webdriver.Chrome(service=service, options=options)


def _safe_get_text(driver: webdriver.Chrome, locator: tuple[str, str]) -> str:
    try:
        return driver.find_element(*locator).text.strip()
    except NoSuchElementException:
        return ''


def _extract_reviews(driver: webdriver.Chrome) -> List[str]:
    reviews: List[str] = []
    try:
        xpath = "//div[contains(@class, 'review')]"
        for review in driver.find_elements(By.XPATH, xpath):
            text = review.get_attribute('innerText') or ''
            cleaned = text.strip()
            if cleaned:
                reviews.append(cleaned)
    except NoSuchElementException:
        pass
    return reviews


def scrape_product_details(url: str) -> Dict[str, str | List[str]]:
    with _create_driver() as driver:
        try:
            driver.get(url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[@id='productTitle']"))
            )
        except TimeoutException as exc:
            raise RuntimeError('Unable to load product details from the supplied URL.') from exc

        price_locator = "//span[contains(@class, 'a-price-whole') or contains(@class, 'a-offscreen') ]"
        details: Dict[str, str | List[str]] = {
            'name': _safe_get_text(driver, (By.XPATH, "//span[@id='productTitle']")),
            'price': _safe_get_text(driver, (By.XPATH, price_locator)),
            'description': _safe_get_text(driver, (By.XPATH, "//h3[@class='product-facts-title']"))
            or _safe_get_text(driver, (By.ID, 'productDescription')),
            'reviews': _extract_reviews(driver),
            'url': url,
        }
    return details


def is_ecommerce_url(url: str) -> bool:
    known_domains = ('amazon', 'ebay', 'walmart', 'bestbuy')
    domain = urlparse(url).netloc
    return any(domain and token in domain.lower() for token in known_domains)


def _invoke_model(prompt: str) -> str:
    if not openai.api_key:
        raise RuntimeError('OPENAI_API_KEY is not configured.')

    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'You are a helpful e-commerce copilot.'},
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=500,
    )
    return response.choices[0].message.content.strip()


def format_product_details(product_details: Dict[str, str | List[str]]) -> str:
    review_preview = ', '.join(product_details.get('reviews', []))
    prompt = (
        'Format the following product details in a customer friendly tone.\n'
        f"Name: {product_details.get('name', '')}\n"
        f"Price: {product_details.get('price', '')}\n"
        f"Description: {product_details.get('description', '')}\n"
        f"URL: {product_details.get('url', '')}\n"
        f"Reviews: {review_preview}"
    )
    return _invoke_model(prompt)


def generate_recommendations(user_preferences: str, product_details: Dict[str, str | List[str]]) -> str:
    prompt = (
        "The shopper's stated preferences are: "
        f"{user_preferences}. Recommend alternative products based on "
        f"the current item (Name: {product_details.get('name', '')}, "
        f"Price: {product_details.get('price', '')}, URL: {product_details.get('url', '')})."
    )
    return _invoke_model(prompt)


def analyze_sentiment(reviews: List[str]) -> Dict[str, int]:
    summary = {'positive': 0, 'negative': 0, 'neutral': 0}
    for review in reviews:
        polarity = TextBlob(review).sentiment.polarity
        if polarity > 0:
            summary['positive'] += 1
        elif polarity < 0:
            summary['negative'] += 1
        else:
            summary['neutral'] += 1
    return summary


def format_sentiment_analysis(sentiments: Dict[str, int]) -> str:
    prompt = (
        'Make this sentiment breakdown readable for non-technical users.\n'
        f"Positive: {sentiments['positive']}\n"
        f"Negative: {sentiments['negative']}\n"
        f"Neutral: {sentiments['neutral']}"
    )
    return _invoke_model(prompt)


def chatbot_response(user_query: str, product_details: Dict[str, str | List[str]]) -> str:
    prompt = (
        f"Customer question: {user_query}\n"
        'Base your answer on the product context below and highlight unknowns.\n'
        f"Product name: {product_details.get('name', '')}\n"
        f"Price: {product_details.get('price', '')}\n"
        f"URL: {product_details.get('url', '')}"
    )
    return _invoke_model(prompt)


def main() -> None:
    st.set_page_config(page_title='E-commerce Product Analyzer')
    st.title('E-commerce Product Analyzer')

    if not openai.api_key:
        st.warning('Set the OPENAI_API_KEY environment variable to enable AI-powered features.')

    url = st.text_input('Enter the product URL:')
    user_preferences = st.text_area(
        "Describe the shopper's preferences",
        placeholder="Looking for high-quality, breathable cotton T-shirts for daily wear",
    )

    if st.button('Analyze Product'):
        if not url:
            st.error('Provide a valid product URL to continue.')
        elif not is_ecommerce_url(url):
            st.error('Only major e-commerce URLs are supported in this demo (e.g., Amazon, eBay).')
        else:
            with st.spinner('Scraping product details...'):
                try:
                    product_details = scrape_product_details(url)
                except Exception as exc:  # pylint: disable=broad-except
                    st.error(str(exc))
                else:
                    st.session_state['product_details'] = product_details
                    st.subheader('Product Details')
                    st.write(format_product_details(product_details))

                    sentiments = analyze_sentiment(product_details.get('reviews', []))
                    if any(sentiments.values()):
                        st.subheader('Sentiment Snapshot')
                        st.write(format_sentiment_analysis(sentiments))
                    else:
                        st.info('No reviews were detected on the page.')

                    if user_preferences:
                        st.subheader('Tailored Recommendations')
                        st.write(generate_recommendations(user_preferences, product_details))

    user_query = st.text_input('Ask a question about the product:')
    if st.button('Get Response'):
        product_details = st.session_state.get('product_details')
        if not product_details:
            st.error('Run the product analysis first to load context.')
        elif not user_query:
            st.error('Enter a question to interact with the assistant.')
        else:
            st.subheader('Assistant Response')
            st.write(chatbot_response(user_query, product_details))


if __name__ == '__main__':
    main()
