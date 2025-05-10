# This file handles user authorization through login and signup
from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from website.database import usersCol
from Routes.init import login_manager
from .user import User  # Import User class
from website.database import usersCol # import user list from database


auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    # Ensure the user is retrieved from the database
    """
    This function loads a user from the database using their ID.
    It is used by Flask-Login to manage user sessions.
    """
    user_data = usersCol.find_one({"_id": ObjectId(user_id)})  # Use ObjectId if IDs are stored as such
    if user_data:
        return User(str(user_data['_id']), user_data['username'], user_data['access'])
    return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route for authenticating users.
    GET request returns the login form.
    POST request processes login credentials.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve user from database
        user_data = usersCol.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password):
            # Pass a valid User object to login_user
            user = User(str(user_data['_id']), user_data['username'], user_data['access'])
            login_user(user)  # Log in the user
            print(f"Logged in as: {current_user.username} (ID: {current_user.id}) Access: {current_user.access}")
            return redirect(url_for('questionnaire_start'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Sign-up route for creating new user accounts.
    GET request returns the registration form.
    POST request processes new user registration.
    """ 
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Save user to the database
        if usersCol.find_one({"username": username}):
            error_message = " Username already exist. Please try again."
            return render_template('signup.html', error_message=error_message)

        usersCol.insert_one({"username": username, "password": hashed_password})
        return redirect(url_for('auth.login'))

    return render_template('signup.html')

@auth.route('/logout')
def logout():
    
    # Logout route that ends the current user session and redirects to login page.
    
    logout_user()
    return redirect(url_for('auth.login'))