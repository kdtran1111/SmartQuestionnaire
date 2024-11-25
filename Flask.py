from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Replace the following with your MongoDB Atlas connection string
client = MongoClient("mongodb+srv://kdtran1111:Danh.2001@cluster0.uz0bc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["questionnaire_db"]
collection = db["responses"]

@app.route('/')
def index():
    # Sample questions from the MAST section of the questionnaire
    questions = [
        {"id": 0, "question": "Do you enjoy a drink now and then?", "yes_no": None},
        {"id": 1, "question": "Do you feel you are a normal drinker or drug user?", "yes_no": None},
        {"id": 2, "question": "Have you ever awakened after drinking or drug use and found that you could not remember a part of what happened?", "yes_no": None},
        # Add more questions as needed
    ]
    return render_template('questionnaire.html', questions=questions)

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve responses from the form
    responses = []
    for key, value in request.form.items():
        responses.append({"question_id": key, "response": value})
    
    # Insert responses into MongoDB
    collection.insert_one({"responses": responses})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
