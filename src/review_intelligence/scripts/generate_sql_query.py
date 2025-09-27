import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_sql_query(user_query):
    # Define the column names in your table schema
    column_names = {
        'name': 'name',
        'location': 'location',
        'date': 'date',
        'rating': 'rating',
        'review': 'review',
        'vector': 'vector'
    }
    
    # Prepare the prompt to ensure GPT-3.5-turbo uses the correct column names and PostgreSQL syntax
    prompt = (
        f"Generate a PostgreSQL SQL query to retrieve reviews based on this user query: {user_query}\n\n"
        f"The table 'reviews' has the following columns with the updated schema:\n"
        f"- {column_names['name']}: TEXT (the name of the reviewer)\n"
        f"- {column_names['location']}: TEXT (the location of the reviewer in 2 letter american state codes)\n"
        f"- {column_names['date']}: TEXT (the date of the review, formatted as a string)\n"
        f"- {column_names['rating']}: TEXT (the rating given by the reviewer, formatted as a string)\n"
        f"- {column_names['review']}: TEXT (the text of the review)\n"
        f"- {column_names['vector']}: FLOAT8[] (a vector representation of the review, stored as an array of FLOAT8)\n"
        f"Generate only the SQL query with PostgreSQL syntax. Ensure the query is not enclosed in backticks or any other markup. Return only the pure SQL query text without any additional explanation or formatting."
    )

    # Generate the SQL query using OpenAI's GPT-3.5-turbo model with chat completions
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in generating SQL queries for PostgreSQL databases."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0
    )
    
    # Extract and return only the pure SQL query text
    sql_query = response.choices[0].message['content'].strip()
    
    # Ensure there are no backticks or extra characters
    sql_query = sql_query.replace('```', '').strip()

    print(sql_query)
    
    return sql_query
