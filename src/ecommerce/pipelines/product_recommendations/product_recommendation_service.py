from __future__ import annotations

import ast
from pathlib import Path
from typing import List

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_PATH = REPO_ROOT / 'data' / 'raw' / 'bigbasket_products_updated.csv'
MODEL_DIR = REPO_ROOT / 'data' / 'processed' / 'recommendations'
VECTORIZER_PATH = MODEL_DIR / 'tfidf_vectorizer.pkl'
COSINE_PATH = MODEL_DIR / 'cosine_similarity_matrix.pkl'

MODEL_DIR.mkdir(parents=True, exist_ok=True)


def _load_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f'Dataset not found at {DATA_PATH}. Please place the cleaned BigBasket CSV in data/raw.'
        )
    data = pd.read_csv(DATA_PATH)
    required_columns = {'product', 'brand', 'description'}
    missing = required_columns - set(data.columns)
    if missing:
        raise ValueError(f'Missing required columns in dataset: {missing}')
    return data.dropna(subset=list(required_columns))


def _parse_list_column(series: pd.Series) -> pd.Series:
    def _to_list(value: str) -> List[str]:
        if isinstance(value, list):
            return value
        try:
            return list(ast.literal_eval(value))
        except (ValueError, SyntaxError):
            return []
    return series.fillna('[]').apply(_to_list)


def _prepare_dataset() -> pd.DataFrame:
    df = _load_data().copy()
    df['description'] = (
        df['description']
        .astype(str)
        .str.lower()
        .str.replace(r'[^\w\s]', '', regex=True)
    )
    for column in ['Products viewed', 'Products purchased', 'Search queries', 'Ratings given']:
        if column in df.columns:
            df[column] = _parse_list_column(df[column])
        else:
            df[column] = [[] for _ in range(len(df))]
    return df


def _load_or_train_models(df: pd.DataFrame) -> tuple[TfidfVectorizer, pd.DataFrame]:
    if VECTORIZER_PATH.exists() and COSINE_PATH.exists():
        with VECTORIZER_PATH.open('rb') as handle:
            vectorizer = pickle.load(handle)
        with COSINE_PATH.open('rb') as handle:
            cosine_matrix = pickle.load(handle)
    else:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=10_000)
        tfidf_matrix = vectorizer.fit_transform(df['description'])
        cosine_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        with VECTORIZER_PATH.open('wb') as handle:
            pickle.dump(vectorizer, handle)
        with COSINE_PATH.open('wb') as handle:
            pickle.dump(cosine_matrix, handle)
    return vectorizer, cosine_matrix


def recommend_products(user_index: int, num_recommendations: int = 5) -> pd.DataFrame:
    data = _prepare_dataset()
    if user_index < 0 or user_index >= len(data):
        raise IndexError('User index out of range for the dataset.')

    _, cosine_matrix = _load_or_train_models(data)
    similarities = list(enumerate(cosine_matrix[user_index]))

    # Incorporate simple interaction boosts
    viewed = set(data.iloc[user_index]['Products viewed'])
    purchased = set(data.iloc[user_index]['Products purchased'])

    boosted_scores = []
    for idx, score in similarities:
        boosted = float(score)
        product_name = data.iloc[idx]['product']
        if product_name in viewed:
            boosted *= 1.2
        if product_name in purchased:
            boosted *= 1.5
        boosted_scores.append((idx, boosted))

    boosted_scores = sorted(boosted_scores, key=lambda item: item[1], reverse=True)
    recommended_indices = [idx for idx, _ in boosted_scores[1 : num_recommendations + 1]]
    return data.iloc[recommended_indices][['product', 'description']]


def main() -> None:
    try:
        user_idx = int(input('Enter a user index to find recommendations: '))
    except ValueError:
        print('Please provide a numeric user index.')
        return

    try:
        recommendations = recommend_products(user_idx)
    except Exception as exc:  # pylint: disable=broad-except
        print(f'Unable to generate recommendations: {exc}')
    else:
        print('Recommended Products:')
        print(recommendations.to_string(index=False))


if __name__ == '__main__':
    main()
