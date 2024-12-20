from datetime import timedelta
from flask import Flask
from flask_login import LoginManager




login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    # login_manager = LoginManager()
    app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a secure key
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)  # Optional: session lifetime

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login page if unauthorized


    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS only)

    return app