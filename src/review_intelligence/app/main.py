import streamlit as st
from scripts.generate_sql_query import generate_sql_query
from scripts.execute_query import execute_sql_query
from scripts.analyze_reviews import analyze_reviews

st.set_page_config(
    page_title="BuckStar Review Analysis",
)

# Title of the app
st.title('BuckStar Review Analysis App')

# Text input for the user query
user_query = st.text_input("Enter your analysis request:")

# Button to submit the query
if st.button('Analyze'):
    # Generate SQL query based on user input
    sql_query = generate_sql_query(user_query)
    
    # Execute the SQL query to fetch reviews
    reviews = execute_sql_query(sql_query)
    
    # Analyze the fetched reviews
    analysis, review_text = analyze_reviews(reviews)
    
    # Display the generated SQL query
    st.write("SQL Query:", sql_query)
    
    # Display the analysis result
    st.write("Analysis:", analysis)


else:
    # Placeholder text when no query has been submitted yet
    st.write("Please enter your analysis request above.")
