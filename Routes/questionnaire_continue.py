from flask import render_template, request, redirect, url_for
from flask_login import login_required, current_user
from bson import ObjectId
from website.database import responsesCol, questionnaireCol



def init_questionnaire_continue_routes(app):
    @app.route('/questionnaire_continue/<response_id>', methods=['GET', 'POST'])
    @login_required
    def questionnaire_continue(response_id):
        # Load questionnaire from MongoDB instead of a JSON file
        # Made sure it's the questionnaire and not Pre/Post Test by the Title
        questionnaire_data = list(questionnaireCol.find({"Title": "Screening Packet Questionnaire"}))

        # Fetch the saved response from the database
        response = responsesCol.find_one({"_id": ObjectId(response_id), "user_id": current_user.id})

        if not response:
            return redirect(url_for('questionnaire_start'))  # Redirect if no response found

        # Remove metadata fields for rendering
        response.pop("_id", None)
        response.pop("user_id", None)

        sections = questionnaire_data[0].get("Sections") if questionnaire_data else {}

        if request.method == 'POST':
            # Iterate over sections and update response object
            for section, content in sections.items():
                if section not in response:
                    response[section] = {}  # Ensure section exists before updating

                if isinstance(content, dict):  # Handle nested sections like ADHS Part A/B
                    for subsection, questions in content.items():
                        if subsection not in response[section]:
                            response[section][subsection] = {}

                        for question in questions:
                            if "question_text" in question:  # Ensure 'question_text' exists
                                question_key = f"{section}_{subsection}_{question['question_text']}"

                                # Check if 'question_type' exists before using it
                                if "question_type" in question:
                                    # Handle multiple choice and multiple choice with other
                                    if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                        response[section][subsection][question["question_text"]] = {
                                            "selected": request.form.getlist(question_key),
                                            "other": request.form.get(f"{question_key}_other", "")
                                        }

                                    # Handle boolean_with_text type
                                    elif question["question_type"] == "boolean_with_text":
                                        response[section][subsection][question["question_text"]] = {
                                            "value": request.form.get(question_key),
                                            "additional": {
                                                field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}", "")
                                                for field in question.get("additional_fields", [])
                                            }
                                        }

                                    # Handle subquestions properly
                                    elif "subquestions" in question:
                                        response[section][subsection][question["question_text"]] = {}
                                        for subquestion in question["subquestions"]:
                                            sub_key = f"{question_key}_{subquestion['question_text']}"
                                            response[section][subsection][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key, "")

                                    # Handle regular fields
                                    else:
                                        response[section][subsection][question["question_text"]] = request.form.get(question_key, "")

                                # If 'question_type' is missing but 'subquestions' exist, handle them separately
                                elif "subquestions" in question:
                                    response[section][subsection][question["question_text"]] = {}
                                    for subquestion in question["subquestions"]:
                                        sub_key = f"{question_key}_{subquestion['question_text']}"
                                        response[section][subsection][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key, "")

                else:  # Handle non-nested sections like A.B.I.
                    for question in content:
                        if "question_text" in question:
                            question_key = f"{section}_{question['question_text']}"

                            # Check if 'question_type' exists before using it
                            if "question_type" in question:
                                if question["question_type"] in ["multiple_choice", "multiple_choice_with_other"]:
                                    response[section][question["question_text"]] = {
                                        "selected": request.form.getlist(question_key),
                                        "other": request.form.get(f"{question_key}_other", "")
                                    }

                                elif question["question_type"] == "boolean_with_text":
                                    response[section][question["question_text"]] = {
                                        "value": request.form.get(question_key, ""),
                                        "additional": {
                                            field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}", "")
                                            for field in question.get("additional_fields", [])
                                        }
                                    }

                                elif "subquestions" in question:
                                    response[section][question["question_text"]] = {}
                                    for subquestion in question["subquestions"]:
                                        sub_key = f"{question_key}_{subquestion['question_text']}"
                                        response[section][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key, "")

                                # Handle "choose_one"
                                elif question["question_type"] == "choose_one":
                                    response[section][question["question_text"]] = request.form.get(question_key) or response[section].get(question["question_text"], "")

                                # Handle "choose_one_with_other"
                                elif question["question_type"] == "choose_one_with_other":
                                    selected_value = request.form.get(question_key) or response[section].get(question["question_text"], {}).get("selected", "")
                                    other_value = request.form.get(f"{question_key}_other") if selected_value == "Other" else ""
                                    response[section][question["question_text"]] = {
                                        "selected": selected_value,
                                        "other": other_value
                                    }
                                # Handle Multiple Data Entry
                                elif question["question_type"] == "multiple_data_entry":
                                    response[section][question["question_text"]] = {
                                        "additional": {
                                                field["field_name"]: request.form.get(f"{question_key}_{field['field_name']}", "")
                                                for field in question.get("additional_fields", [])
                                            }
                                    }

                                else:
                                    response[section][question["question_text"]] = request.form.get(question_key, "") 

                            # If 'question_type' is missing but 'subquestions' exist, handle them separately
                            elif "subquestions" in question:
                                response[section][question["question_text"]] = {}
                                for subquestion in question["subquestions"]:
                                    sub_key = f"{question_key}_{subquestion['question_text']}"
                                    response[section][question["question_text"]][subquestion["question_text"]] = request.form.get(sub_key, "")

                    print("DEBUGGING RESPONSE BEFORE SAVING: \n", response)

            responsesCol.update_one(
                {"_id": ObjectId(response_id)},
                {"$set": response}
            )
            return redirect(url_for('questionnaire_start'))

        # Render the form pre-filled with saved responses
        return render_template('questionnaire_continue.html', title="Continue Questionnaire", sections=sections, response=response, response_id=response_id)
