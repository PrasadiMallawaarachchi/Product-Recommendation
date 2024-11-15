import pickle
import streamlit as st
import numpy as np



collaborative_filtering_model = pickle.load(open('artifacts/collaborative_filtering_model.pkl', 'rb'))
cosine_similarities_content = pickle.load(open('artifacts/cosine_similarities_content.pkl', 'rb'))
knn_model_data = pickle.load(open('artifacts/knn_model.pkl', 'rb'))
Product_names = pickle.load(open('artifacts/Product_names.pkl', 'rb'))
suggested_products_basedOnTime = pickle.load(open('artifacts/seasonal_picks.pkl', 'rb'))
tfidf_vectorizer = pickle.load(open('artifacts/tfidf_vectorizer.pkl', 'rb'))
trending_products = pickle.load(open('artifacts/trending_products.pkl', 'rb'))
updated_products = pickle.load(open('artifacts/updated_products.pkl', 'rb'))
user_item_matrix = pickle.load(open('artifacts/user_item_matrix.pkl', 'rb'))



print("Begin")