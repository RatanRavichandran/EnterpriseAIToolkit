import pandas as pd
import random
from datetime import datetime, timedelta

# Define food and drinks
food_drinks = [
    {"name": "Caramel Macchiato", "ingredients": ["espresso", "vanilla syrup", "steamed milk", "caramel sauce"], "taste_profile": "sweet and creamy"},
    {"name": "Blueberry Muffin", "ingredients": ["flour", "blueberries", "sugar", "egg", "milk"], "taste_profile": "sweet and moist"},
    {"name": "Classic Espresso", "ingredients": ["espresso"], "taste_profile": "rich and bold"},
    {"name": "Avocado Toast", "ingredients": ["bread", "avocado", "salt", "pepper", "lemon juice"], "taste_profile": "creamy and savory"},
    {"name": "Green Tea", "ingredients": ["green tea leaves", "water"], "taste_profile": "fresh and earthy"}
]

# Generate sales data
sales_data = []
start_date = datetime.now() - timedelta(days=30)  # Sales for the past 30 days

for _ in range(100):  # Generate 100 sales records
    item = random.choice(food_drinks)
    date = start_date + timedelta(days=random.randint(0, 30))
    quantity = random.randint(1, 5)
    price_per_item = round(random.uniform(2.5, 7.5), 2)
    sales_data.append({
        "item_name": item["name"],
        "quantity": quantity,
        "date": date.strftime("%Y-%m-%d"),
        "total_price": round(quantity * price_per_item, 2)
    })

# Convert to DataFrame
food_drinks_df = pd.DataFrame(food_drinks)
sales_data_df = pd.DataFrame(sales_data)

# Export to CSV
food_drinks_df.to_csv('data/buckstars_food_drinks.csv', index=False)
sales_data_df.to_csv('data/buckstars_sales.csv', index=False)

print("CSV files have been created: 'buckstars_menu.csv' and 'buckstars_sales.csv'")
