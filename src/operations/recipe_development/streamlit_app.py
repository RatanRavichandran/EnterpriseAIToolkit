import streamlit as st
import pandas as pd
import openai
import os
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()

    # Set up OpenAI API key
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Streamlit app title
    st.title('BuckStars Recipe Analysis')

    # Load default menu data
    @st.cache_data
    def load_menu_data():
        return pd.read_csv('data/buckstars_food_drinks.csv')

    menu_data = load_menu_data()

    # Upload and load sales data
    uploaded_file = st.file_uploader("Upload your sales data CSV", type="csv")
    if uploaded_file is not None:
        sales_data = pd.read_csv(uploaded_file)
    else:
        st.warning("Please upload a CSV file.")
        st.stop()

    # Analyze sales performance
    sales_summary = sales_data.groupby('item_name').agg({'quantity': 'sum'}).sort_values(by='quantity', ascending=False)
    st.write("### Most Popular Items Based on Sales Quantity")
    st.dataframe(sales_summary)

    # Display ingredients and taste profiles for popular items
    st.write("### Ingredients and Taste Profiles for Popular Items")
    popular_items = sales_summary.index[:5]
    popular_ingredients = []
    popular_taste_profiles = []
    
    ingredients_profiles = []
    
    for item in popular_items:  # Analyze top 5 items
        item_details = menu_data[menu_data['name'] == item]
        if not item_details.empty:
            ingredients = item_details.iloc[0]['ingredients']
            taste_profile = item_details.iloc[0]['taste_profile']
            ingredients_profiles.append({
                'Item': item,
                'Ingredients': ', '.join(eval(ingredients)),  # Unpack ingredients list into text
                'Taste Profile': taste_profile
            })
            popular_ingredients.extend(eval(ingredients))  # Collecting ingredients for new recipe generation
            popular_taste_profiles.append(taste_profile)  # Collecting taste profiles
    
    st.dataframe(pd.DataFrame(ingredients_profiles))

    # Generate new recipes based on popular ingredients and taste profiles
    if st.button("Generate New Recipe Ideas"):
        try:
            prompt = (
                f"Create 2-3 unique recipes using these popular ingredients: {', '.join(set(popular_ingredients))} "
                f"with taste profiles: {', '.join(set(popular_taste_profiles))}."
            )
            messages = [
                {"role": "system", "content": """
                "You are a top barista for a coffee company called BuckStars. Using the provided list of popular ingredients and taste profiles, create unique and creative coffee-based recipes. Each recipe should be well-balanced and effectively use the ingredients. Please format your response as follows:

- Title: [Name of the Recipe]
- Ingredients: [List the ingredients used]
- Instructions: [Step-by-step preparation instructions]
- Taste Profile: [Describe the flavor and sensory experience]"

                """},
                {"role": "user", "content": prompt}
            ]
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            
            recipe_text = response.choices[0].message['content'].strip()
            
            st.write("### Generated Recipe Ideas")
            st.markdown(recipe_text.replace('\n', '<br>').replace('- ', '<br>- '), unsafe_allow_html=True)
        except Exception as e:
            st.error("Failed to generate recipe due to an error with OpenAI service.")
            st.error(str(e))

if __name__ == '__main__':
    main()
