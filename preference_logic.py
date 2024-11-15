import pandas as pd
import streamlit as st

def fetch_user_preferences(user_id, engine):
    query = f"""
    SELECT preference_type, preference_value
    FROM userpreferences
    WHERE user_id = {user_id}
    """
    preferences = pd.read_sql(query, con=engine)
    return preferences if not preferences.empty else None

def recommend_based_on_preferences(preferences, engine):
    conditions = []
    params = []

    for _, row in preferences.iterrows():
        preference_type = row['preference_type']
        preference_value = row['preference_value']
        
        if preference_type.lower() == 'brand':
            conditions.append("Brand LIKE %s")
            params.append(f"%{preference_value}%")
        elif preference_type.lower() == 'category':
            conditions.append("Category LIKE %s")
            params.append(f"%{preference_value}%")
    
    if conditions:
        query_conditions = " OR ".join(conditions)
        query = f"SELECT * FROM all_products WHERE {query_conditions}"

        try:
            recommended_products = pd.read_sql(query, con=engine, params=tuple(params))

            # CSS Styling for the product container
            st.markdown(
                """
                <style>
                <style>
                .preference-product-container {
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                    padding: 10px;
                    height: 250px;
                }
                .preference-product-image {
                    width: 120px;
                    height: 150px;
                    object-fit: cover;
                    border-radius: 10px;
                }
                </style>
                """, 
                unsafe_allow_html=True
            )

            # Display recommended products
            if not recommended_products.empty:
                cols = st.columns(5)

                for i, product in enumerate(recommended_products.head(5).iterrows()):
                    # Directly using markdown to create styled containers
                    _, product = product
                    with cols[i]:
                        st.text(f"{product['Name']}")
                        

                        st.markdown(f'''
                            <div class="preference-product-container">
                                <img src="{product['ImageURL']}" class="preference-product-image">
                                <div>{product['Brand']}</div>
                                <div>{product['Category']}</div>
                               
                            </div>
                            ''', unsafe_allow_html=True)
                        


            else:       
                st.write("No products found based on your preferences.")
        except Exception as e:
            st.write(f"Error fetching recommended products: {e}")
