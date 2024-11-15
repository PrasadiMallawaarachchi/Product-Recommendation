import streamlit as st
import sqlalchemy
import pandas as pd
import user_management
from streamlit_modal import Modal
import base64


# Database connection
DATABASE_URI = 'mysql+pymysql://root:1234@localhost/product_recommendations'
engine = sqlalchemy.create_engine(DATABASE_URI)


# Redirect functions
def redirect_to_app():
    import appguest  
    appguest.main(username=st.session_state['username'])  

def redirect_to_guest_app():
    import appguest  
    appguest.main()

# Initialize modals for alerts
success_modal = Modal(title="You're in!", key="success_modal")

# Convert local image to base64
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Add background image from local file
def add_bg_from_local(image_path):
    base64_image = get_base64_image(image_path)
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("data:image/png;base64,{base64_image}");
             background-size: cover;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )


def main():
    add_bg_from_local('img7.jpg')

    if 'username' not in st.session_state:
        st.session_state['username'] = None

    st.title("Welcome to Product Recommendations - Login/Signup")

    menu = ["Login", "Signup"]
    choice = st.selectbox("Choose Action", menu)

    if choice == "Signup":
        st.subheader("Create New Account")
        signup_form()
    elif choice == "Login":
        st.subheader("Login to Your Account")
        login_form()
    
    # Handle success modal for login/signup
    if success_modal.is_open():
        with success_modal.container():
            st.write(f"Login/Signup successful, {st.session_state['username']}!")
            if st.button("Proceed to App"):
                success_modal.close()  
                redirect_to_app() 


# Signup form
def signup_form():
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Signup"):
        if username and password:
            # Check if username already exists
            existing_users_query = f"SELECT username FROM users WHERE username='{username}'"
            existing_users = pd.read_sql(existing_users_query, con=engine)
            if not existing_users.empty:
                st.error("Username already exists. Please choose a different username.")
            else:
                # Insert new user into the database
                new_user_id = user_management.generate_user_id()
                user_management.add_user(new_user_id, username, password)
                st.success(f"Signup successful! Your user ID is {new_user_id}.")
                
                # Store username and user_id in session state
                st.session_state['username'] = username
                st.session_state['user_id'] = new_user_id
                st.session_state['logged_in'] = True  # Mark as logged in
                st.session_state['page'] = 'main'     # Set the page state to main

        else:
            st.error("Please fill out both fields.")




# Login form
def login_form():
    login_method = st.radio("Login using:", ["User ID", "Username"])

    if login_method == "User ID":
        user_id = st.text_input("User ID")
        if st.button("Login"):
            # Assume password is not needed for User ID login
            if user_management.validate_user_by_id(user_id):  # You may need to adjust this function
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user_id
                st.session_state['username'] = user_management.get_username_by_id(user_id)
                st.session_state['page'] = 'main'  # Set the page state
                st.success(f"Welcome back, {st.session_state['username']}!")
                
            else:
                st.error("Invalid User ID.")
    else:
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            if user_management.verify_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['user_id'] = user_management.get_user_id_by_username(username)
                st.session_state['page'] = 'main'  # Set the page state
                st.success(f"Welcome back, {username}!")
            else:
                st.error("Invalid Username or Password.")



# Run the main function
if __name__ == '__main__':
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False

    if st.session_state['logged_in']:
        import appguest  # Import the main app module
        appguest.main(username=st.session_state['username'])  # Call main in appguest with username
    else:
        main()  # Show the login/signup page if not logged in
