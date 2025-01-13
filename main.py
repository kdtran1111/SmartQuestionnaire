from sympy import content
from bson import ObjectId
from website import create_app
from website.database import db, responsesCol, questionnaireCol, usersCol  # Import database collections
from flask import flash, render_template, request, redirect, url_for, session 
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
                                elif question["question_type"] == "boolean_with_text":  # Handle boolean_with_text
                                    responses[section][subsection][question["question_text"]] = {
                                        "value": request.form.get(question_key),
                                        "additional": {
                                            field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                                            for field in question["additional_fields"]
                                        }
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
                            elif question["question_type"] == "boolean_with_text":  # Handle boolean_with_text
                                responses[section][question["question_text"]] = {
                                    "value": request.form.get(question_key),
                                    "additional": {
                                        field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                                        for field in question["additional_fields"]
                                    }
                                }
                            elif "subquestions" in question:  # Handle subquestions
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


#route to the screen to choose questionnaire
@app.route('/questionnaireStart', methods=['GET'])
@login_required
def questionnaire_start():
    # Check if the user has any saved responses in the collection
    user_responses = list(responsesCol.find({"user_id": current_user.id}))

    # Format the responses for display
    formatted_responses = [
        {"id": str(response["_id"]), "date": response["_id"].generation_time.strftime("%Y-%m-%d %H:%M:%S")}
        for response in user_responses
    ]

    return render_template(
        'questionnaire_start.html',
        title="Questionnaire Start",
        responses=formatted_responses
    )

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
        return f"Logged in as: {current_user.username} (ID: {current_user.id}) Access: {current_user.access}"
    return "Not logged in."

@app.route('/debug-session')
def debug_session():
    return str(session)



@app.route('/questionnaire_continue/<response_id>', methods=['GET', 'POST'])
@login_required
def questionnaire_continue(response_id):
    # Fetch the saved response from the database
    response = responsesCol.find_one({"_id": ObjectId(response_id), "user_id": current_user.id})

    if not response:
        return redirect(url_for('questionnaire_start'))  # Redirect if no response found

    # Remove metadata fields for rendering
    response.pop("_id", None)
    response.pop("user_id", None)

    sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

    if request.method == 'POST':
        # Update the saved response with new inputs from the form
        for section, content in sections.items():
            if isinstance(content, dict):  # Handle nested sections like ADHS Part A/B
                for subsection, questions in content.items():
                    if isinstance(question, dict) and "question_text" in question:  # Check if question has 'question_text'
                        for question in questions:
                            question_key = f"{section}_{subsection}_{question['question_text']}"
                            if "question_type" in question:
                                if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                    response[section][subsection][question["question_text"]] = {
                                        "selected": request.form.getlist(question_key),
                                        "other": request.form.get(f"{question_key}_other")
                                    }
                                elif question["question_type"] == "boolean_with_text":
                                    response[section][subsection][question["question_text"]] = {
                                        "value": request.form.get(question_key),
                                        "additional": {
                                            field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                                            for field in question["additional_fields"]
                                        }
                                    }
                                elif "subquestions" in question:
                                    response[section][subsection][question["question_text"]] = {}
                                    for subquestion in question["subquestions"]:
                                        sub_key = f"{question_key}_{subquestion['question_text']}"
                                        response[section][subsection][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key)
                                else:
                                    response[section][subsection][question["question_text"]] = request.form.get(question_key)
            else:  # Handle regular sections
                for question in content:
                    if "question_text" in question:  # Ensure 'question_text' exists
                        question_key = f"{section}_{question['question_text']}"
                        if "question_type" in question:
                            if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                response[section][question["question_text"]] = {
                                    "selected": request.form.getlist(question_key),
                                    "other": request.form.get(f"{question_key}_other")
                                }
                            elif question["question_type"] == "boolean_with_text":
                                response[section][question["question_text"]] = {
                                    "value": request.form.get(question_key),
                                    "additional": {
                                        field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                                        for field in question["additional_fields"]
                                    }
                                }
                            elif "subquestions" in question:
                                response[section][question["question_text"]] = {}
                                for subquestion in question["subquestions"]:
                                    sub_key = f"{question_key}_{subquestion['question_text']}"
                                    response[section][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key)
                            else:
                                response[section][question["question_text"]] = request.form.get(question_key)

        # Save updated response to MongoDB
        responsesCol.update_one({"_id": ObjectId(response_id)}, {"$set": response})
        return redirect(url_for('questionnaire_start'))

    # Render the form pre-filled with saved responses
    return render_template('questionnaire_continue.html', title="Continue Questionnaire", sections=sections, response=response, response_id=response_id)
#debug Flask Routing
@app.cli.command()
def list_routes():
    import urllib
    from flask import current_app
    output = []
    for rule in current_app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        output.append(f"{rule.endpoint:50s} {methods:20s} {urllib.parse.unquote(str(rule))}")
    for line in sorted(output):
        print(line)



#This helps start the app correctly, make sure it is alway on the bottom
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)