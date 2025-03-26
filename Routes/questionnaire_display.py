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
                section_totals={},  # Empty dictionary for section totals
                total_yes=0,
                total_no=0,
                message="No responses found."
            )

        latest_response.pop('_id', None)  # Remove MongoDB's internal '_id' field

        # Initialize counts
        section_results = {}
        section_totals = {}
        total_yes = 0
        total_no = 0

        # Grading Criteria Dictionary
        grading_criteria = {
            "MAST": {  # Add points for each "Yes"
                
                "0": 0,
                "1" : 2,
                "2" : 2,
                "3" : 1,
                "4" : 2,
                "5" : 1,
                "6" : 2,
                "7" : 2,
                "8" : 5,
                "9" : 1,
                "10" : 2,
                "11" : 2,
                "12" : 2,
                "13" : 2,
                "14" : 2,
                "15" : 2,
                "16" : 1,
                "17" : 2,
                "18" : 2,    #for this question, if vision/voice worth 2 pts, shake worth 5. But for the purpose of this, keep it as yes/no for 2 points
                "19" : 5,
                "20" : 5,
                "21" : 2,
                "22" : 2,
                "23" : 2,
                "24" : 2,

                #"default": 1  # If no specific criteria, add 1 point for "Yes"
            },
            "A.B.I.": {  # Example of another section with custom grading
                "1": 2,  # Question 1 is worth 2 points if "Yes"
                "2": 1,  # Question 2 is worth 1 point if "Yes"
                "default": 0.5  # All other questions worth 0.5 points if "Yes"
            },
            # Define more sections with different grading criteria here
        }

        # Count "Yes" and "No" answers for each section and overall
        for section, questions in latest_response.items():
            if isinstance(questions, dict):  # Ensure we are iterating over valid question data
                section_yes = 0
                section_no = 0
                section_score = 0  # Initialize section score

                for question_text, answer in questions.items():
                    question_number = None
                    
                    # Extract question number if present (e.g., "0) Do you enjoy a drink now and then?")
                    if question_text.strip() and ")" in question_text:
                        try:
                            question_number = question_text.split(")")[0].strip()
                        except ValueError:
                            pass  # If not found, leave question_number as None

                    # Check if the answer is a nested dictionary with a "value" key
                    if isinstance(answer, dict):
                        if "value" in answer:
                            if answer["value"] == "Yes":
                                section_yes += 1
                                total_yes += 1

                                # Apply grading logic
                                if section in grading_criteria:
                                    if question_number in ["23", "24"]:
                                        number_of_times = int(answer["additional"]["Number of Times"])
                                        section_score += grading_criteria[section].get(question_number, 0) * number_of_times     
                                    else:    
                                        if question_number and question_number in grading_criteria[section]:
                                            section_score += grading_criteria[section][question_number]
                                        else:
                                            section_score += grading_criteria[section].get("default", 0)
                            
                            elif answer["value"] == "No":
                                section_no += 1
                                total_no += 1

                                # Apply grading logic
                                if section in grading_criteria:
                                    if question_number and question_number in grading_criteria[section]:
                                        section_score += grading_criteria[section][question_number]
                                    else:
                                        section_score += grading_criteria[section].get("default", 0)
                    
                    # If the answer is a direct string response
                    elif isinstance(answer, str):
                        if answer == "Yes":
                            section_yes += 1
                            total_yes += 1
                            # Apply grading logic
                            if section in grading_criteria:
                                if question_number and question_number in grading_criteria[section]:
                                    section_score += grading_criteria[section][question_number]
                                else:
                                    section_score += grading_criteria[section].get("default", 0)
                        
                        elif answer == "No":
                            section_no += 1
                            total_no += 1

                            # Apply grading logic
                            if section in grading_criteria:
                                if question_number and question_number in grading_criteria[section]:
                                    section_score += grading_criteria[section][question_number]
                                else:
                                    section_score += grading_criteria[section].get("default", 0)
                    
                section_results[section] = {"yes": section_yes, "no": section_no, "score" : section_score}
                section_totals[section] = section_score  # Save section score separately

        # Render the results
        return render_template(
            'questionnaire_display.html',
            section_results=section_results,
            section_totals=section_totals,  # Include section totals
            total_yes=total_yes,
            total_no=total_no
        )

