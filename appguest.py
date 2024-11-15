import streamlit as st
import numpy as np
import pandas as pd
from data_upload import (
    knn_model_data, 
    user_item_matrix, 
    updated_products, 
    cosine_similarities_content, 
    Product_names
)
#st.set_page_config(page_title="Product Recommendations", layout="wide")
import sqlalchemy
import os
from datetime import datetime
import base64
from preference_logic import fetch_user_preferences, recommend_based_on_preferences  # Import the functions
from sqlalchemy import create_engine


# Replace with your actual database connection details
DATABASE_URI = 'mysql+pymysql://root:1234@localhost/product_recommendations'

# Create an engine
engine = sqlalchemy.create_engine(DATABASE_URI)

def set_background_image():
    # Get the path of the current working directory
    current_directory = os.path.dirname(__file__)
    background_image_path = os.path.join(current_directory, 'img7.jpg')
    
    # Open the image and convert to base64
    with open(background_image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    # Set the background image
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpeg;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            height: 100vh;  /* Ensure it covers the full height */
        }}
        </style>
        """, unsafe_allow_html=True
    )

# Function to handle logout
def logout():
    if 'logged_in' in st.session_state:
        del st.session_state['logged_in']
    if 'username' in st.session_state:
        del st.session_state['username']
    



# Create database engine (adjust the connection string as needed)
engine = create_engine(DATABASE_URI)

# Main function
def main(username=None):
    set_background_image()

    # If the user is logged in, show "Logout" button
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.sidebar.button("Logout", on_click=logout)
        st.sidebar.write(f"Welcome {st.session_state['username']}")
    else:
        # If not logged in, show the "Menu" (login) button
        st.sidebar.button("Menu", on_click=lambda: st.session_state.update(page='login'))
        st.sidebar.write(f"Welcome {username or 'Guest'}")

    # Header for main page
    st.header('Product Recommender System')

    
    search_term = st.selectbox('Search for a product:', Product_names)
    num_recommendations = st.slider('Select number of recommendations:', min_value=1, max_value=10, value=5)
    

    # Custom CSS to style the sidebar
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #250840;
        }
        </style>
        """, unsafe_allow_html=True
    )

    

    # KNN model logic for collaborative filtering
    def get_collaborative_based_recommendations(selected_product, top_n):
        product_id = updated_products[updated_products['Name'] == selected_product].index[0]
        distance, suggestion = knn_model_data.kneighbors(user_item_matrix.iloc[product_id, :].values.reshape(1, -1), n_neighbors=top_n)
        col_recommended_products = user_item_matrix.index[suggestion[0]]
        return col_recommended_products

    # Content-based filtering recommendations
    def get_content_based_recommendations(Name, top_n):
        index = updated_products[updated_products['Name'] == Name].index[0]
        similarity_scores = cosine_similarities_content[index]
        similar_indices = similarity_scores.argsort()[::-1][1:top_n + 1]
        content_recommended_products = updated_products.loc[similar_indices, 'Name'].values
        return content_recommended_products

    # Hybrid recommendations combining collaborative and content-based filtering
    def hybrid_recommendations(selected_product, top_n):
        col_recommended_products = get_collaborative_based_recommendations(selected_product, top_n)
        content_recommended_products = get_content_based_recommendations(selected_product, top_n)

        col_recommended_products = [str(Name).replace("'", "") for Name in col_recommended_products if isinstance(Name, str)]
        content_recommended_products = [str(Name).replace("'", "") for Name in content_recommended_products if isinstance(Name, str)]
        
        products_name = list(set(col_recommended_products) | set(content_recommended_products))
        products_name = products_name[:top_n]
        
        products = updated_products[updated_products['Name'].isin(products_name)]
        product_names = products['Name'].tolist()
        product_urls = products['ImageURL'].tolist()
        product_genres = products['Category'].tolist()
        product_ratings = products['Price'].tolist()

        return product_names, product_urls, product_genres, product_ratings

    # Themed placeholder image for products
    placeholder_image_url = "https://dummyimage.com/120x150/cccccc/000000&text=Beauty+Product"

    # Custom CSS for product styling
    st.markdown(
        """
        <style>
        .product-container {
            height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .product-image {
            width: 120px;
            height: 150px;
            object-fit: cover;
            border-radius: 10px;
        }
        .product-genres {
            margin-top: 2px;
            text-align: center;
            white-space: normal;
            word-wrap: break-word;
            line-height: 1.2;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Button to show recommendations based on selected product
    if st.button('Show Recommendation'):
        recommended_products, product_url, product_genres, product_rating = hybrid_recommendations(search_term, num_recommendations)
        cols = st.columns(num_recommendations)

        for i in range(num_recommendations):
            image_url = product_url[i] if product_url[i] else placeholder_image_url
            
            with cols[i]:
                st.markdown(f'<div class="product-container"><img src="{image_url}" class="product-image"><div class="product-genres">{product_genres[i]}</div></div>', unsafe_allow_html=True)
                st.text(recommended_products[i])
                if st.button(f'Buy', key=f'buy_{i}'):
                    st.write("Are you sure you want to buy?")
                    st.success(f"You have selected to buy {recommended_products[i]}!")
    # Adding a border after the button
    st.markdown("""
        <style>
        .border-after-button {
            border-top: 3px solid orange;
            margin-top: 20px;
            padding-top: 10px;
        }
        </style>
        <div class="border-after-button"></div>
        """, unsafe_allow_html=True)
    


    # Function to display greeting based on current time
    def display_greeting():
        # Get the current hour
        now = datetime.now()
        current_hour = now.hour

        # Determine the greeting based on the hour
        if 5 <= current_hour < 12:
            greeting = "Good Morning! Start your day with some great recommendations!"
        elif 12 <= current_hour < 17:
            greeting = "Good Afternoon! Discover some amazing products to brighten your day"
        elif 17 <= current_hour < 21:
            greeting = "Good Evening! Wind down with our top picks for tonight."
        else:
            greeting = "Good Night! Explore our late-night offers."

        st.sidebar.write(greeting)

    # Call the function to display the greeting
    display_greeting()

    def display_star_rating(rating):
        full_star = "⭐"  # Unicode star character
        empty_star = "☆"  # Unicode empty star character
        return full_star * int(rating) + empty_star * (5 - int(rating))
    
    import requests

    # Define the Flask API URL for seasonal picks 
    API_URL = "http://127.0.0.1:5000/suggestions"

    # Sidebar for Seasonal Picks
    
    if st.sidebar.button('🌟 Seasonal Picks'):
        
        # Fetch data from Flask backend
        try:
            response = requests.get(API_URL)
            response.raise_for_status()  # Check for request errors
            suggested_products_basedOnTime = response.json()  # Parse the JSON response
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching seasonal picks: {e}")
            suggested_products_basedOnTime = []

        # Check if we have any seasonal picks
        if suggested_products_basedOnTime:
            st.subheader("Seasonal Picks")
            # Create columns for displaying products
            cols = st.columns(5)
            for i, product in enumerate(suggested_products_basedOnTime[:20]):
                with cols[i % 5]:
                    st.text(product.get('Name', 'Unnamed Product'))
                    st.markdown(f'<img src="{product["ImageURL"]}" class="product-image" style="width: 100%;">', unsafe_allow_html=True)
                    st.write(f" {product.get('Category', 'Unknown Category')}")
                    st.write(display_star_rating(product.get("Rating", 0)))
        else:
            st.write("No seasonal picks available.")

    if st.sidebar.button("❤ Wishlist"):
        st.sidebar.write("Your Wishlist")

    if st.sidebar.button('💬 View My Feedbacks'):
            st.sidebar.write("Your Feedbacks")

    if st.sidebar.button('🎁 Giftcards'):
            st.sidebar.write("Your Giftcards")

    if st.sidebar.button('💳 Wallet'):
            st.sidebar.write("Your Wallet")

    if st.sidebar.button("📦 Past Orders"):
            st.sidebar.write("Your Past Orders")

    if st.sidebar.button("🤝 Referrals"):
            st.sidebar.write("Your Referrals")

        # Help Section
    if st.sidebar.button("❓ Help"):
            st.sidebar.write("Help Section")

    if st.sidebar.button('❓ FAQ'):
            st.sidebar.write("Frequently Asked Questions")




    # Show preference-based recommendations only if user is logged in
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        st.subheader("Tailored Suggestions Just for You")

        # Fetch user preferences from the database
        user_id = st.session_state['user_id']
        preferences = fetch_user_preferences(user_id, engine)  # Pass the user_id and engine to fetch preferences

        if preferences is not None and not preferences.empty:
            recommend_based_on_preferences(preferences, engine)

    st.markdown("""
        <style>
        .border-after-preferences {
            border-top: 3px solid orange;
            margin-top: 20px;
            padding-top: 10px;
        }
        </style>
        <div class="border-after-preferences"></div>
        """, unsafe_allow_html=True)

    # Load trending products from SQL
    trending_products_query = "SELECT * FROM trending_products"
    trending_products = pd.read_sql(trending_products_query, con=engine)


    # Display trending products
    def display_trending_products():
        st.subheader("Top Trending Products")
        cols = st.columns(5)
        for i, row in trending_products.head(20).iterrows():
            image_url = row['ImageURL'] if row['ImageURL'] else placeholder_image_url
            
            with cols[i % 5]:
                st.text(row['Name'])
                st.markdown(f'''
                    <div class="product-container">
                        <img src="{image_url}" class="product-image">
                        <div class="product-genres">{row["Brand"]}</div>
                        <div class="product-genres">{display_star_rating(row["Rating"])}</div>
                    </div>
                ''', unsafe_allow_html=True)
               
                if st.button(f'Buy ', key=f'buy_trending_{i}'):
                    st.success(f"You have selected to buy {row['Name']}!")

    display_trending_products()

    

   # Load all products from SQL
    all_products_query = "SELECT * FROM all_products"
    all_products = pd.read_sql(all_products_query, con=engine)

    # Display all products
    def display_all_products():
        st.subheader("All Products")
        cols = st.columns(5)
        for i, row in all_products.head(20).iterrows():
            image_url = row['ImageURL'] if row['ImageURL'] else placeholder_image_url
            
            with cols[i % 5]:
                st.text(row['Name'])
                st.markdown(f'''
                    <div class="product-container">
                        <img src="{image_url}" class="product-image">
                        <div class="product-genres">{row["Brand"]}</div>
                        <div class="product-genres">{row["Category"]}</div>
                        <div class="product-genres">{display_star_rating(row["Rating"])}</div>
                    </div>
                ''', unsafe_allow_html=True)
                rating = 4  # Example rating (out of 5)
                if st.button(f'Buy ', key=f'buy_all_{i}'):
                    st.success(f"You have selected to buy {row['Name']}!")

    # Call the function to display all products
    display_all_products()


# Function to redirect to the login page
def redirect_to_login():
    st.session_state['page'] = 'login'  # Set a session state variable to indicate the current page


# Ensure to call main() when running as a standalone
if __name__ == '__main__':
    if 'page' in st.session_state and st.session_state['page'] == 'login':
        import login  # Import your login module
        login.main()  # Call the main function in login.py
    else:
        main()
