README


Before you begin, ensure you have the following installed:
    - bcrypt   (for password hashing )
    - flask-session (for sessions of user authentication)
    - flask-limiter (for limiting wrong attempts for login)
    - flask-login (for login library)
    - `pip` (Python package manager)
    - sympy (for math operations)
    - Installation of SSL certificate might also be require for some OS
        - using: pip install --upgrade certifi


Setup:
    - Install dependencies packages:
        pip install Flask Flask-Login Flask-WTF wtforms

Start the App:
    - Run the command:
        python main.py
    - Open you browser of choice and navigate to the URL below:
        http://127.0.0.1:5000


Folder Structure:

/Capstone

|--/routes
    |-- auth.py                                 # authentication/User Mixing
    |-- debug.py                                # Debug
    |-- index.py                                # Home page
    |-- init.py                                     # Initializes Flask app with login and route blueprints.   
    |-- questionnaire.py                        # Start new questionnaire
    |-- questionnaire_display.py                # Display the questionnaire Result/ graded
    |-- questionnaire_start.py                  # Choose to continue a saved questionnaire or start a new questionnaire
    |-- questionnaire_continue.py               # Continue the saved questionnaire
    |-- user.py                                 # User Mixin
    |-- views.py                                
|--/website
    |--/templates
        |-- base.html                               # Base setup for html display
        |-- index.html                              # Home page
        |-- questionnaire.html                      # Questionnaire page
        |-- questionnaire_display.html              # Display the questionnaire Result/ graded
        |-- questionnaire_start.html                # The page to choose to continue a saved questionnaire or start a new questionnaire
        |-- questionnaire_continue.html             # The page to continue the saved questionnaire
        |-- login.html                              # Login page
        |-- signup.html                             # Registration page
        
    |--/static                                      # Layout setting for pages
        |--/images                                  # Hold the images of the Agency and screening information    
    |-- database.py                                 # Set up database link, can be changed to a different database by changing the link 
    
|--/Documentation
    |--DatabaseQuestionInput.json                   # The questions for the quiz
    |--extracted_text.txt                           # The txt file extracted from questionnaire
    |--extractPDF.py                                # Code to extract text from PDF
    |--Screening packet 08312020.pdf                # The Screening Quiz
    |--README.md                                    # README file for Setup and Execution



|-- main.py                                         # Run all the routes



Notes: The basic client's information for this questionnaire does not fully work. Because I did not account for a few of the question_type