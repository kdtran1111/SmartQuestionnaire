from flask import render_template
from website.database import responsesCol

def init_questionnaire_display_routes(app):
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
