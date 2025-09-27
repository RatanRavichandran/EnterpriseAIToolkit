import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import openai
from textblob import TextBlob
import os

# Web Scraping Code
def scrape_product_details(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        product_details = {
            'name': soup.find('span', id='productTitle').text.strip(),
            'price': soup.find('span', class_='a-price-whole').text.strip(),
            'description': soup.find('h3', class_='product-facts-title').text.strip(),
            'reviews': [review.get_text().strip() for review in soup.find_all('div', class_='review')],
            'url': url  # Capture the product URL
        }
        return product_details

    except Exception as e:
        print(f"Error occurred during the request: {e}")

# Remaining functions and main block remain unchanged


def is_ecommerce_url(url):
    ecom_domains = ['amazon', 'ebay', 'walmart', 'bestbuy']
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    for ecom_domain in ecom_domains:
        if ecom_domain in domain:
            return True
    return False

# GPT-4o Integration
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_recommendations(user_preferences, product_details):
    product_info = f"Product Name: {product_details['name']}\nPrice: {product_details['price']}\nURL: {product_details['url']}"
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Based on the user's preferences: {user_preferences}, recommend similar products. Here is the product info: {product_info}"}
        ],
        max_tokens=150
    )
    
    return response.choices[0].message.content.strip()

# Comparison Tools
def compare_products(product1, product2):
    comparison = {
        'name': (product1['name'], product2['name']),
        'price': (product1['price'], product2['price']),
        'features': {
            'feature1': (product1['features']['feature1'], product2['features']['feature1']),
            'feature2': (product1['features']['feature2'], product2['features']['feature2']),
        },
        'url': (product1['url'], product2['url'])  # Include URLs in the comparison
    }
    return comparison

# Sentiment Analysis
def analyze_sentiment(reviews):
    sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
    for review in reviews:
        analysis = TextBlob(review)
        if analysis.sentiment.polarity > 0:
            sentiments['positive'] += 1
        elif analysis.sentiment.polarity < 0:
            sentiments['negative'] += 1
        else:
            sentiments['neutral'] += 1
    return sentiments

# Chatbot
def chatbot_response(user_query, product_details):
    product_info = f"Product Name: {product_details['name']}\nPrice: {product_details['price']}\nURL: {product_details['url']}"
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{user_query}\nHere is the product info: {product_info}"}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Main Function
def main():
    url = 'https://www.amazon.in/Levis-Mens-Regular-T-Shirt-16960-1206_Blue/dp/B0CRVJ9DXM/?_encoding=UTF8&pd_rd_w=xLtf8&content-id=amzn1.sym.f8b2fc0c-779f-43a6-b25a-069849dd23a6%3Aamzn1.symc.fc11ad14-99c1-406b-aa77-051d0ba1aade&pf_rd_p=f8b2fc0c-779f-43a6-b25a-069849dd23a6&pf_rd_r=PTC1AH1P3H3F0FT6J4CX&pd_rd_wg=D4HDh&pd_rd_r=2d4685dd-0eb9-4e2a-8ae4-5a7d8a2b1d44&ref_=pd_hp_d_atf_ci_mcx_mr_ca_hp_atf_d'
    
    if is_ecommerce_url(url):
        product_details = scrape_product_details(url)
        print(json.dumps(product_details, indent=2))
        
        user_preferences = "User likes high-quality tshirts."
        recommendations = generate_recommendations(user_preferences, product_details)
        print("Recommendations:\n", recommendations)
        
        sentiments = analyze_sentiment(product_details['reviews'])
        print("Sentiment Analysis:\n", sentiments)
        
        user_query = "What is the material of thsi tshirt?"
        chatbot_resp = chatbot_response(user_query, product_details)
        print("Chatbot Response:\n", chatbot_resp)
    else:
        print("The provided URL is not from an e-commerce site.")

if __name__ == "__main__":
    main()
