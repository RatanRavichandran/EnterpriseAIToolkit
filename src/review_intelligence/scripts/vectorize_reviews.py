import pandas as pd
from sentence_transformers import SentenceTransformer

# Load your data
df = pd.read_csv('/Users/shriyansarkal/food_and_drink/review_analysis/data/raw/reviews.csv')

# Vectorize the reviews
model = SentenceTransformer('all-MiniLM-L6-v2')
df['vector'] = df['Review'].apply(lambda x: model.encode(x))

# Save the vectorized data
df.to_csv('/Users/shriyansarkal/food_and_drink/review_analysis/data/processed/vectorized_reviews.csv', index=False)
