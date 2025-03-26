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
|--/website
    |--/templates
        |-- base.html                               # Base setup for html display
        |-- index.html                              # Home page
        |-- questionnaire.html                      # Questionnaire page
        |-- questionnaire_display.html              # Display the questionnaire Result/ graded
        |-- questionnaireStart.html                 # The page to choose to continue a saved questionnaire or start a new questionnaire
        |-- questionnaire_continue.html             # The page to continue the saved questionnaire
        |-- login.html                              # Login page
        |-- register.html                           # Registration page
        
|--/static                                      # Layout setting for pages
    |--
|--/Documentation
    |--DatabaseQuestionInput.json                   # The questions for the quiz
    |--extracted_text.txt                           # The txt file extracted from questionnaire
    |--extractPDF.py                                # Code to extract text from PDF
    |--Screening packet 08312020.pdf                # The Screening Quiz
    |--README.md                                    # README file for Setup and Execution

|--main.py                                          # Main application