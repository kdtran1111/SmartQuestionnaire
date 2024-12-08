README


Setup:

    - Install Python
    - Install dependencies packages:
        pip install Flask Flask-Login Flask-WTF wtforms

Start the App:
    - Run the command:
        python Flask.py
    - Open you browser of choice and navigate to the URL below:
        http://127.0.0.1:5000

Folder Structure:

/Capstone
|--/templates
    |-- index.html                              # Home page
    |-- questionnaire.html                      # Questionnaire page
    |-- login.html                              # Login page
    |-- register.html                           # Registration page
|--/static                                      # Layout setting for pages
    |--
|--DatabaseQuestionInput.json                   # The questions for the quiz
|--extracted_text.txt                           # The txt file extracted from questionnaire
|--extractPDF.py                                # Code to extract text from PDF
|--Flask.py                                     # Main application
|--Screening packet 08312020.pdf                # The Screening Quiz
|--README.md                                    # README file for Setup and Execution