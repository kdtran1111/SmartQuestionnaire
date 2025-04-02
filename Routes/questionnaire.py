from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from website.database import responsesCol, questionnaireCol

def init_questionnaire_routes(app):
    @app.route('/questionnaire', methods=['GET', 'POST'])
    @login_required
    def questionnaire():
        # Load questionnaire from MongoDB instead of a JSON file
        # Made sure it's the questionnaire and not Pre/Post Test by the Title
        questionnaire_data = list(questionnaireCol.find({"Title": "Screening Packet Questionnaire"}))
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

                                # Handle "choose_one"
                                elif question["question_type"] == "choose_one":
                                    responses[section][question["question_text"]] = request.form.get(question_key)

                                # Handle "choose_one_with_other"
                                elif question["question_type"] == "choose_one_with_other":
                                    responses[section][question["question_text"]] = {
                                        "selected": request.form.get(question_key),
                                        "other": request.form.get(f"{question_key}_other") if request.form.get(question_key) == "Other" else ""
                                    }
                                elif question["question_type"] == "multiple_data_entry":
                                    if "additional_fields" in question:  # Ensure the key exists before accessing
                                        responses[section][question["question_text"]] = {
                                            "additional": {
                                                field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}")
                                                for field in question["additional_fields"]
                                            }
                                        }
                                    
                                else:
                                    responses[section][question["question_text"]] = request.form.get(question_key)

            # Save the collected responses to MongoDB
            insert_result = responsesCol.insert_one(responses)
            response_id = str(insert_result.inserted_id)
            return redirect(url_for('questionnaire_display', response_id=response_id))

        return render_template('questionnaire.html', title=questionnaire_data[0]["Title"], sections=sections)
