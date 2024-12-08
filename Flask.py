from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Replace the following with your MongoDB Atlas connection string
client = MongoClient("mongodb+srv://kdtran1111:Danh.2001@cluster0.uz0bc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["questionnaire_db"]
responsesCol = db["responses"]
questionnaireCol = db['questions']
usersCol = db['users']

# Load questionnaire from MongoDB instead of a JSON file
questionnaire_data = list(questionnaireCol.find({}))

# Optional: Remove `_id` from each question, if needed
for question in questionnaire_data:
    question.pop('_id', None)

# Assuming the structure of `questionnaire_data` from MongoDB matches the previous JSON file
@app.route('/')
def index():
    title = questionnaire_data[0].get("Title") if questionnaire_data else "No Title Available"
    return render_template('index.html', title=title)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Collect login credentials
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Authenticate the user against the database
        user = usersCol.find_one({"username": username, "password": password})
        if user:
            return redirect(url_for('questionnaire'))
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)
    
    return render_template('login.html')


@app.route('/questionnaire', methods=['GET', 'POST'])
def questionnaire():
    # Assuming that sections are embedded in the first document
    sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

    if request.method == 'POST':
        # Collect answers
        responses = {}
        for section, questions in sections.items():
            responses[section] = {}
            for question in questions:
                question_key = question["question_text"]
                if question["question_type"] == "multiple_data_entry":
                    responses[section][question_key] = {
                        field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                        for field in question["fields"]
                    }
                else:
                    responses[section][question_key] = request.form.get(question_key)

        # Save to MongoDB
        responsesCol.insert_one(responses)
        return redirect('/')
    
    return render_template('questionnaire.html', title=questionnaire_data[0]["Title"], sections=sections)

if __name__ == '__main__':
    app.run(debug=True)
