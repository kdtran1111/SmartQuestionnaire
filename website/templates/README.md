### Prerequisites
Before you begin, ensure you have the following installed:
- Python 3.7+
- bcrypt   (for password hashing )
- flask-session (for sessions of user authentication)
- flask-limiter (for limiting wrong attempts for login)
- flask-login (for login library)
- `pip` (Python package manager)

### Usage
1. Install the required dependencies:
   ```bash
   pip install Flask Flask-Login Flask-WTF wtforms

2. Running the Application
Start the Flask app:

   ```bash
   python app.py
   
3. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Project Structure
Here are the most *prominent* files for this code
   ```
   /project_folder
   ├── app.py                  # Main Flask application file
   ├── users.json              # JSON file storing user data
   ├── /templates              # HTML templates for rendering pages
   │   ├── index.html          # Home page
   │   ├── login.html          # Login page
   │   ├── register.html       # Registration page
   ├── /static
   │   ├── /images             # Static images folder
   │       └── AI.jpg
```
