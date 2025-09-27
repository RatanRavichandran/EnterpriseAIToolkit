import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def analyze_reviews(reviews):
    # Print the first review tuple for debugging
    print("First review tuple:", reviews[0])
    
    # Concatenate all review texts, clearly separating them
    reviews_text = "\n\n".join([f"Review {i+1}: {review}" for i, (_, _, _, _, _, review, _) in enumerate(reviews)])
    print("Concatenated reviews text:")
    print(reviews_text)
    
    # Generate analysis using OpenAI's GPT-3.5-turbo model
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": """
            You are an expert in sentiment analysis. For each review provided below, give a detailed sentiment analysis. Analyze the tone, emotion, and overall sentiment of each review separately. Provide a summary of the sentiment for each review.
            """},
            {"role": "user", "content": f"Here are the reviews:\n\n{reviews_text}"}
        ],
        max_tokens=1000
    )
    
    # Return the analysis text from the response
    return response.choices[0].message['content'].strip(), reviews_text
