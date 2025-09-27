from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = Path(__file__).resolve().parents[4] / 'data' / 'reference' / 'personalized_ecommerce'
USERS_PATH = DATA_DIR / 'users.csv'
PRODUCTS_PATH = DATA_DIR / 'products.csv'
INTERACTIONS_PATH = DATA_DIR / 'interactions.csv'
FEEDBACK_PATH = Path('feedback.csv')


def _load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f'Missing input dataset: {path}. Place the sample files in data/reference/personalized_ecommerce.'
        )
    return pd.read_csv(path)


def _build_models() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    users_df = _load_dataset(USERS_PATH)
    products_df = _load_dataset(PRODUCTS_PATH)
    interactions_df = _load_dataset(INTERACTIONS_PATH)
    interactions_df = interactions_df.drop_duplicates(subset=['user_id', 'product_id'], keep='last')
    return users_df, products_df, interactions_df


def _create_user_item_matrix(interactions_df: pd.DataFrame) -> pd.DataFrame:
    return interactions_df.pivot(index='user_id', columns='product_id', values='rating').fillna(0)


def _build_embeddings(matrix: pd.DataFrame) -> pd.DataFrame:
    svd = TruncatedSVD(n_components=min(len(matrix), 50), random_state=42)
    return pd.DataFrame(svd.fit_transform(matrix), index=matrix.index)


class CollaborativeFilteringDemo:
    def __init__(self) -> None:
        self.users, self.products, interactions = _build_models()
        self.user_item_matrix = _create_user_item_matrix(interactions)
        self.user_embeddings = _build_embeddings(self.user_item_matrix)
        self.feedback = pd.DataFrame(columns=['user_id', 'product_id', 'feedback'])

    def get_recommendations(self, user_id: int, num_recommendations: int = 5) -> pd.DataFrame:
        if user_id not in self.user_item_matrix.index:
            raise KeyError(f'User {user_id} not found in the dataset.')

        user_vector = self.user_item_matrix.loc[user_id].values.reshape(1, -1)
        similarities = cosine_similarity(user_vector, self.user_item_matrix.values)
        ranked_indices: List[int] = similarities.argsort()[0][::-1][1 : num_recommendations + 1]
        product_ids = self.user_item_matrix.columns[ranked_indices].tolist()
        return self.products[self.products['product_id'].isin(product_ids)]

    def collect_feedback(self, user_id: int, product_id: int, feedback: str) -> None:
        new_feedback = pd.DataFrame({'user_id': [user_id], 'product_id': [product_id], 'feedback': [feedback]})
        self.feedback = pd.concat([self.feedback, new_feedback], ignore_index=True)
        self.feedback.to_csv(FEEDBACK_PATH, index=False)

    def get_adjusted_recommendations(self, user_id: int, num_recommendations: int = 5) -> pd.DataFrame:
        recommendations = self.get_recommendations(user_id, num_recommendations * 2)
        product_ids = recommendations['product_id'].tolist()

        user_feedback = self.feedback[self.feedback['user_id'] == user_id]
        for _, row in user_feedback.iterrows():
            if row['feedback'] == 'down' and row['product_id'] in product_ids:
                product_ids.remove(row['product_id'])
            elif row['feedback'] == 'up' and row['product_id'] not in product_ids:
                product_ids.insert(0, row['product_id'])

        trimmed_ids = product_ids[:num_recommendations]
        return self.products[self.products['product_id'].isin(trimmed_ids)]


def main() -> None:
    demo = CollaborativeFilteringDemo()
    sample_user_id = demo.user_item_matrix.index[0]
    print(f'Using sample user ID: {sample_user_id}')

    recs = demo.get_adjusted_recommendations(sample_user_id)
    print('\nInitial Recommendations:\n', recs)

    if not recs.empty:
        demo.collect_feedback(sample_user_id, int(recs.iloc[0]['product_id']), 'up')
        if len(recs) > 1:
            demo.collect_feedback(sample_user_id, int(recs.iloc[1]['product_id']), 'down')

    print('\nAdjusted Recommendations after Feedback:\n', demo.get_adjusted_recommendations(sample_user_id))


if __name__ == '__main__':
    main()
