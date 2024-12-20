
'''
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from website.database import usersCol  # Import users collection

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Collect login credentials
        username = request.form.get('username')
        password = request.form.get('password')

        # Find user in the database
        user = usersCol.find_one({"username": username})
        if user and check_password_hash(user['password'], password):
            # Store user information in the session
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            return redirect(url_for('questionnaire'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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
    # Clear session data
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('auth.login'))

'''


from bson import ObjectId
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from website.database import usersCol
from website import login_manager
from .user import User  # Import User class
from website.database import usersCol # import user list from database


auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    # Ensure the user is retrieved from the database
    user_data = usersCol.find_one({"_id": ObjectId(user_id)})  # Use ObjectId if IDs are stored as such
    if user_data:
        return User(str(user_data['_id']), user_data['username'])
    return None

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Retrieve user from database
        user_data = usersCol.find_one({"username": username})
        if user_data and check_password_hash(user_data['password'], password):
            # Pass a valid User object to login_user
            user = User(str(user_data['_id']), user_data['username'])
            login_user(user)  # Log in the user
            return redirect(url_for('questionnaire'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)

    return render_template('login.html')

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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
    logout_user()
    return redirect(url_for('auth.login'))