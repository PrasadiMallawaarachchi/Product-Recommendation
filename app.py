import streamlit as st
import numpy as np
import pandas as pd
from data_upload import knn_model_data, user_item_matrix, updated_products, cosine_similarities_content, Product_names, suggested_products_basedOnTime
import sqlalchemy
import os
from datetime import datetime


# Replace with your actual database connection details
DATABASE_URI = 'mysql+pymysql://root:1234@localhost/product_recommendations'





# Your app's existing code


# Your app's existing code


# Create an engine
engine = sqlalchemy.create_engine(DATABASE_URI)

# Display the image at a specific point in your app
image_path = os.path.join(os.getcwd(), 'image2.jpg')  # Update with your image filename
st.image(image_path, use_column_width=True)

# Function to display current date and time
def display_current_datetime():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time as desired
    formatted_date = now.strftime("%Y-%m-%d")
    formatted_time = now.strftime("%H:%M:%S")  # Format: YYYY-MM-DD HH:MM:SS
    st.sidebar.write(f" Date : {formatted_date}")
    st.sidebar.write(f" Time: {formatted_time}")

# Call the function to display date and time in the sidebar
display_current_datetime()

# Function to truncate text for UI
def truncate_text(text, max_length=10):
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

# Header for main page
st.markdown('<h1 class="custom-header">Product Recommender System</h1>', unsafe_allow_html=True)


# **Remove the product selection from the sidebar**
# Moved the product selection to the main page.
search_term = st.selectbox('Search for a product:', Product_names, key='search_term', label_visibility="collapsed")

# Search products
def search_products(search_term):
    if search_term:
        # Filter the products based on the search term
        results = updated_products[updated_products['Name'].str.contains(search_term, case=False, na=False)]
        return results
    return updated_products  # Return all products if no search term

# Get search results
search_results = search_products(search_term)

# **Remove the sidebar product selection**
# No longer in the sidebar. Instead, we handle recommendations below based on selected product.

# Custom CSS to style the sidebar
st.markdown(
    """
    <style>

    .custom-header {
        color: black;
    }
    .stSubheader, h2 {
        color: black !important;
    }

    /* Select box styling */
    div[data-baseweb="select"] {
        color: black;
    }

    /* Product name and category styling */
    .product-genres, .stText {
        color: black;
    }

    /* Style for product container text */
    .product-container {
        color: black;
    }

    [data-testid="stSidebar"] {
        background-color: #250840;
    }
    div[data-testid="stAppViewContainer"] {
        background-color: white;
       
    }
    
    /* Buttons and select boxes in main content */
    div[data-testid="stAppViewContainer"] button, 
    div[data-testid="stAppViewContainer"] select, 
    div[data-testid="stAppViewContainer"] .stButton button {
       
        background-color: #AE5ADB;
    }

    /* Sidebar buttons and select boxes text color */
    div[data-testid="stSidebar"] button, 
    div[data-testid="stSidebar"] select {

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

        /* Header styling */
    .stHeader {
        color: black;
    }

    /* Subheader styling (targeting h2 elements) */
    h2 {
        color: black;
    }

    /* Select box styling */
    div[data-baseweb="select"] {
        color: black;
    }

    /* Product name and category styling */
    .product-genres, .stText {
        color: black;
    }

    /* Style for product container text */
    .product-container {
        color: black;
    
    }
    </style>
    """, unsafe_allow_html=True
)





# Seasonal Picks in the sidebar
st.sidebar.header("🌟 Seasonal Picks")
if st.sidebar.button('Show Seasonal Picks'):
    st.write("Showing Seasonal Picks")
    
    if not suggested_products_basedOnTime.empty:
        st.subheader("Seasonal Picks")
        cols = st.columns(5)
        for i, row in suggested_products_basedOnTime.iterrows():
            with cols[i % 5]:
                st.text(row['Name'])
                st.image(row['ImageURL'], width=120)
                st.write(f"Category: {row['Category']}")
    else:
        st.write("No seasonal picks available.")

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


# Now define your header, subheaders, select box, and products sections as usual.

# Button to show recommendations based on selected product
if st.button('Show Recommendation'):
    recommended_products, product_url, product_genres, product_rating = hybrid_recommendations(search_term, 6)
    cols = st.columns(5)

    for i in range(1, 6):
        image_url = product_url[i] if product_url[i] else placeholder_image_url
        
        with cols[i-1]:
            st.markdown(f'<div class="product-container"><img src="{image_url}" class="product-image"><div class="product-genres">{product_genres[i]}</div></div>', unsafe_allow_html=True)
            st.text(recommended_products[i])
            if st.button(f'Buy', key=f'buy_{i}'):
                st.write("Are you sure you want to buy?")
                st.success(f"You have selected to buy {recommended_products[i]}!")

# Load trending products from SQL
trending_products_query = "SELECT * FROM trending_products"
trending_products = pd.read_sql(trending_products_query, con=engine)

# Display trending products
def display_trending_products():
    st.subheader("Top Trending Products")
    cols = st.columns(5)
    for i, row in trending_products.iterrows():
        image_url = row['ImageURL'] if row['ImageURL'] else placeholder_image_url
        
        with cols[i % 5]:
            st.text(row['Name'])
            st.markdown(f'''
                <div class="product-container">
                    <img src="{image_url}" class="product-image">
                    <div class="product-genres">{row["Brand"]}</div>
                    <div class="product-genres">{row["Rating"]}</div>
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
    for i, row in all_products.iterrows():
        image_url = row['ImageURL'] if row['ImageURL'] else placeholder_image_url
        
        with cols[i % 5]:
            st.text(row['Name'])
            st.markdown(f'''
                <div class="product-container">
                    <img src="{image_url}" class="product-image">
                    <div class="product-genres">{row["Brand"]}</div>
                    <div class="product-genres">{row["Category"]}</div>
                </div>
            ''', unsafe_allow_html=True)
           
            if st.button(f'Buy ', key=f'buy_all_{i}'):
                st.success(f"You have selected to buy {row['Name']}!")

# Call the function to display all products
display_all_products()

# Wishlist and Feedback buttons
if st.sidebar.button("❤ Wishlist"):
    st.sidebar.write("Your Wishlist")

if st.sidebar.button('View My Feedbacks'):
    st.sidebar.write("Your Feedbacks")

# Help Section
st.sidebar.button("❓ Help")
if st.sidebar.button('🔍 FAQ'):
    st.sidebar.write("Frequently Asked Questions")
