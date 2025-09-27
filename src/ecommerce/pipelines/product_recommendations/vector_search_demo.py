from __future__ import annotations

import sys
from typing import Dict

import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
}


def scrape_product_details(url: str) -> Dict[str, str]:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    return {
        'name': (soup.select_one('#productTitle') or {}).get_text(strip=True) if soup.select_one('#productTitle') else '',
        'price': (soup.select_one('#corePrice_feature_div span.a-price-whole') or {}).get_text(strip=True)
        if soup.select_one('#corePrice_feature_div span.a-price-whole')
        else '',
        'description': (soup.select_one('#detailBulletsWrapper_feature_div h2') or {}).get_text(strip=True)
        if soup.select_one('#detailBulletsWrapper_feature_div h2')
        else '',
        'reviews': '\n'.join(review.get_text(strip=True) for review in soup.select('#cm_cr_dp_d_rating_histogram div')),
        'url': url,
    }


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python vector_search_demo.py <product_url>')
        return

    url = sys.argv[1]
    try:
        details = scrape_product_details(url)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Failed to scrape product details: {exc}')
    else:
        print(details)


if __name__ == '__main__':
    main()
