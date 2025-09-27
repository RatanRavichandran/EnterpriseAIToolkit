import os
import psycopg2
import pandas as pd
import ast
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database settings from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# Connect to PostgreSQL database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

# Load vectorized reviews
df = pd.read_csv('/Users/shriyansarkal/food_and_drink/review_analysis/data/processed/vectorized_reviews.csv')  # Adjust path if necessary

# Convert vector strings to lists
def convert_vector(vector_str):
    try:
        return ast.literal_eval(vector_str)
    except (ValueError, SyntaxError):
        return []

df['vector'] = df['vector'].apply(convert_vector)

# Insert data into the table
for _, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO reviews (name, location, date, rating, review, vector)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (row['name'], row['location'], row['Date'], row['Rating'], row['Review'], row['vector'])
    )
conn.commit()

cur.close()
conn.close()
