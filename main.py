from sympy import content
from website import create_app
from website.database import db, responsesCol, questionnaireCol, usersCol  # Import database collections
from flask import render_template, request, redirect, url_for, session 
from flask_login import UserMixin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from website.database import usersCol
#from .user import User  # Import the User class

app = create_app()

# Load questionnaire from MongoDB instead of a JSON file
questionnaire_data = list(questionnaireCol.find({}))

# Optional: Remove `_id` from each question, if needed
for question in questionnaire_data:
    question.pop('_id', None)








@app.route('/')
def index():
    title = questionnaire_data[0].get("Title") if questionnaire_data else "No Title Available"
    return render_template('index.html', title=title)


'''
#Questionnaire Display route
@app.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    # Access current user details
    if current_user.is_authenticated:
        username = current_user.username
        print(f"Current User: {username}")
    else:
        return redirect(url_for('auth.login'))

    sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

    if request.method == 'POST':
        responses = {"user_id": current_user.id}  # Attach user ID to responses
        for section, questions in sections.items():
            responses[section] = {}
            for question in questions:
                if "question_text" in question:
                    question_key = question["question_text"]
                    responses[section][question_key] = request.form.get(question_key)

        responsesCol.insert_one(responses)
        return redirect(url_for('questionnaire_display'))

    return render_template('questionnaire.html', title=questionnaire_data[0]["Title"], sections=sections)

'''

'''
@app.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    # Access current user details
    if current_user.is_authenticated:
        username = current_user.username
        print(f"Current User: {username}")
    else:
        return redirect(url_for('auth.login'))

    # Retrieve questionnaire sections
    sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

    if request.method == 'POST':
        responses = {"user_id": current_user.id}  # Attach user ID to responses
        for section, questions in sections.items():
            responses[section] = {}
            for question in questions:
                if "question_text" in question:
                    question_key = question["question_text"]
                    if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                        # Store the selected options and any "other" field
                        responses[section][question_key] = {
                            "selected": request.form.getlist(question_key),  # For checkboxes
                            "other": request.form.get(f"{question_key}_other")  # "Other" field, if applicable
                        }
                    else:
                        responses[section][question_key] = request.form.get(question_key)

        # Save to MongoDB
        responsesCol.insert_one(responses)
        return redirect(url_for('questionnaire_display'))

    return render_template('questionnaire.html', title=questionnaire_data[0]["Title"], sections=sections)
'''

@app.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    if current_user.is_authenticated:
        username = current_user.username
        print(f"Current User: {username}")
    else:
        return redirect(url_for('auth.login'))

    sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

    if request.method == 'POST':
        responses = {"user_id": current_user.id}  # Attach user ID to responses
        for section, content in sections.items():
            if section == "ADHS":  # Handle the ADHS section with nested structure
                responses[section] = {}
                for subsection, questions in content.items():
                    responses[section][subsection] = {}
                    for question in questions:
                        if "question_text" in question:  # Ensure 'question_text' exists
                            question_key = f"{section}_{subsection}_{question['question_text']}"
                            if "question_type" in question:
                                if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                    responses[section][subsection][question["question_text"]] = {
                                        "selected": request.form.getlist(question_key),
                                        "other": request.form.get(f"{question_key}_other")
                                    }
                                elif "subquestions" in question:  # Handle subquestions
                                    responses[section][subsection][question["question_text"]] = {}
                                    for subquestion in question["subquestions"]:
                                        subquestion_key = f"{question_key}_{subquestion['question_text']}"
                                        responses[section][subsection][question["question_text"]][subquestion["question_text"]] = request.form.get(subquestion_key)
                                else:
                                    responses[section][subsection][question["question_text"]] = request.form.get(question_key)
                            elif "subquestions" in question:  # If no question_type but has subquestions
                                responses[section][subsection][question["question_text"]] = {}
                                for subquestion in question["subquestions"]:
                                    subquestion_key = f"{question_key}_{subquestion['question_text']}"
                                    responses[section][subsection][question["question_text"]][subquestion["question_text"]] = request.form.get(subquestion_key)
            else:  # Handle other sections
                responses[section] = {}
                for question in content:
                    if "question_text" in question:
                        question_key = f"{section}_{question['question_text']}"
                        if "question_type" in question:
                            if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                responses[section][question["question_text"]] = {
                                    "selected": request.form.getlist(question_key),
                                    "other": request.form.get(f"{question_key}_other")
                                }
                            elif "subquestions" in question:
                                responses[section][question["question_text"]] = {}
                                for subquestion in question["subquestions"]:
                                    subquestion_key = f"{question_key}_{subquestion['question_text']}"
                                    responses[section][question["question_text"]][subquestion["question_text"]] = request.form.get(subquestion_key)
                            else:
                                responses[section][question["question_text"]] = request.form.get(question_key)

        # Save the collected responses to MongoDB
        responsesCol.insert_one(responses)
        return redirect(url_for('questionnaire_display'))

    return render_template('questionnaire.html', title=questionnaire_data[0]["Title"], sections=sections)


@app.route('/questionnaireDisplay', methods=['GET'])
def questionnaire_display():
    # Fetch the most recent responses from the database
    latest_response = responsesCol.find_one(sort=[("_id", -1)])  # Fetch the most recent document

    if not latest_response:
        # Return with an empty dictionary for section_results
        return render_template(
            'questionnaire_display.html',
            section_results={},  # Empty dictionary
            total_yes=0,
            total_no=0,
            message="No responses found."
        )

    latest_response.pop('_id', None)  # Optional: Remove MongoDB's internal '_id' field

    # Initialize counts
    section_results = {}
    total_yes = 0
    total_no = 0

    # Count "Yes" and "No" answers for each section and overall
    for section, questions in latest_response.items():
        if isinstance(questions, dict):  # Ensure we are iterating over valid question data
            section_yes = 0
            section_no = 0
            for _, answer in questions.items():
                if answer == "Yes":
                    section_yes += 1
                    total_yes += 1
                elif answer == "No":
                    section_no += 1
                    total_no += 1
            section_results[section] = {"yes": section_yes, "no": section_no}

    # Render the results
    return render_template(
        'questionnaire_display.html',
        section_results=section_results,
        total_yes=total_yes,
        total_no=total_no
    )


# For debug
@app.route('/debug')
def debug():
    if current_user.is_authenticated:
        return f"Logged in as: {current_user.username} (ID: {current_user.id})"
    return "Not logged in."

@app.route('/debug-session')
def debug_session():
    return str(session)
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
