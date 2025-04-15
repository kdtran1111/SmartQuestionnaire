from flask import render_template
from website.database import responsesCol
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bson import ObjectId

def init_questionnaire_display_routes(app):
    @app.route('/questionnaireDisplay/<response_id>', methods=['GET', 'POST'])
    def questionnaire_display(response_id):
        # Fetch the most recent responses from the database
        latest_response = responsesCol.find_one({"_id": ObjectId(response_id), "user_id": current_user.id}) # Fetch the most recent document

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
        adhs_A = 0
        adhs_B = 0
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
            "ADHS": {
                "Part A": {
                    "1": 1,
                    "2": 1,
                    "3": 1,
                    "4": 1,
                    "5": 1,
                    "6": {  # Nested questions
                        "Hallucinations": 2,
                        "Convulsive seizures": 1,
                        "Delirium tremens (shakes)": 1
                    },
                    "7": {  # Nested questions
                        "Alcohol liver disease": 2,
                        "Alcoholic pancreatitis": 2,
                        "Alcoholic cardiomyopathy": 2
                    }
                },
                "Part B": {
                    #"1": 1, #these questions (1,2) are not graded
                    #"2": 1,
                    "3": 1,
                    "4": 1,
                    "5": 1,
                    "6": 1,
                    "7": 1,
                    "8": 1,
                    "9": {  # Nested questions
                        "Shakes or malaise relieved by drinking/using": 1,
                        "Irritability": 1,
                        "Nausea (e.g., the next day after drinking)": 1,
                        "Anxiety": 1
                    },
                    "10": 1,
                    "11": 1,
                    "12": 1
                }
            },
            "A_B_I": {  # Example of another section with custom grading
                "1": 1,  # Question 1 is worth 1 points , etc...
                "2": 1,
                "3": 1,
                "4": 1,
                "5": 1,
                "6": 1,
                "7": 1,
                "8": 1,
                "9": 1,
                "10": 1,
                        
                "default": 0.5  # All other questions worth 0.5 points if "Yes"
            },
            "T_V_I": {
               "1": 1,
               "2": 1,
               "3": 1, 
               "4": 1,
               "5": -1   
               # Question 5 Minus 1 for each treatment received. The logic for this question could be change to 
               # reflect the score proportional to the numbers of treatment received for better reflec

            },
            "S_I": {
                # this grading will be handled in the logic below
            },
            "D_I": {
                "1": 1,
                "2": 1,
                "3": 1,
                "4": 1,
                "5": 1,
                "6": 1,
                "7": 1,
                "8": 1,
                "9": 1,
                "10": 1,
            },
            "V_I": {
               "1": {  # Nested questions
                        "1) No Injury": 1,
                        "2) A minor injury with complete recovery in a few days": 2,
                        "3) Injury with complete recovery in a few weeks": 3,
                        "4) Injury with complete recovery in a few months": 4,
                        "5) Disabling Injury": 5,
                        "6) Death": 6
                    } 
            },
            "L_O_F": {
                "1": {
                    "1) Arguing (without threats)": 1,
                    "2) Property damage or yelling (without threats)": 2,
                    "3) Physical contact or threat of contact (push, hold, slaps, restrain, block movement)": 3,
                    "4) Physical force or threat of force (hit, punch, kick, bite, etc)": 4,
                    "5) Weapon display or threat of weapon use (club, knife, gun, etc)": 5,
                    "6) Weapon use, choking or forced sex": 6
                },
                "2": {
                    "1) Arguing (without threats)": 1,
                    "2) Property damage or yelling (without threats)": 2,
                    "3) Physical contact or threat of contact (push, hold, slaps, restrain, block movement)": 3,
                    "4) Physical force or threat of force (hit, punch, kick, bite, etc)": 4,
                    "5) Weapon display or threat of weapon use (club, knife, gun, etc)": 5,
                    "6) Weapon use, choking or forced sex": 6
                }
            },
            "H_I": {

                "default": 1  #each yes is 1 point so I kept it as default instead of declaring each question point
            },
            "D_V_P_I": {
                "default" : 1 #each yes is 1 point so I kept it as default instead of declaring each question point
            }
        
        }

        # Count "Yes" and "No" answers for each section and overall
        for section, questions in latest_response.items():
            if section == "ADHS":
                section_score = 0
                
                section_yes = 0
                section_no = 0
                print("Went into ADHS section\n")

                for part, part_questions in questions.items():  # questions is already ADHS[section]
                    print(f"Went into {part}\n")
                    for question_text, answer in part_questions.items():
                        question_number = None

                        # Extract question number
                        if question_text.strip() and ")" in question_text:
                            try:
                                question_number = question_text.split(")")[0].strip()
                                
                            except ValueError:
                                pass
                        print(f"stripped: {question_number} , {question_text} \n" ) 
                        if isinstance(answer, dict):  # Nested question (e.g., withdrawal symptoms)
                            print("Went into instance Yes\n")
                            for sub_question, sub_answer in answer.items():
                                if sub_answer == "Yes":
                                    sub_score = grading_criteria[section][part].get(question_number, {})
                                    print(f"Grading for ADHS -> {part} -> Question {question_number}: +{grading_criteria[section][part][question_number]}")
                                    if isinstance(sub_score, dict):
                                        #section_score += sub_score.get(sub_question, 0)
                                        section_score += sub_score.get(sub_question, 0)
                                        break           #break so that the score only get added once if any or all of the sub question's answer is "yes"
                                        
                                    else:
                                        section_score += sub_score  # fallback if not nested

                                    section_yes += 1
                                elif sub_answer == "No":
                                    section_no += 1

                        elif answer == "Yes":
                            print("Went into text Yes\n")
                            section_yes += 1
                            if question_number and question_number in grading_criteria[section][part]:
                                section_score += grading_criteria[section][part][question_number]
                                print(f"Grading for ADHS -> {part} -> Question {question_number}: +{grading_criteria[section][part][question_number]}")
                            else:
                                print(f"Grading for ADHS -> {part} -> Question {question_number}: +0")

                        elif answer == "No":
                            section_no += 1
                        print(f"Section Score: {section_score}")
                        if part == "Part A":
                            adhs_A = section_score #Set the total of section score for each Part
                        elif part == "Part B":
                            adhs_B = section_score
                section_results[section] = {
                    "yes": section_yes,
                    "no": section_no,
                    "score": section_score,
                    "adhs_A" : adhs_A,
                    "adhs_B": adhs_B
                }
            
                section_totals[section] = section_score

            
            
            else: #Handle the non-nested sections. i.e. erything except ADHS
                if isinstance(questions, dict):  # Ensure we are iterating over valid question data
                    section_yes = 0
                    section_no = 0
                    section_score = 0  # Initialize section score

                    for question_text, answer in questions.items():
                        question_number = None
                        print(f"Went into {section} in else\n")
                        # Extract question number if present (e.g., "0) Do you enjoy a drink now and then?")
                        if question_text.strip() and ")" in question_text:
                            try:
                                question_number = question_text.split(")")[0].strip()
                            except ValueError:
                                pass  # If not found, leave question_number as None
                        print(f"stripped: {question_number}\n" )            
                        # Check if the answer is a nested dictionary with a "value" key
                        if isinstance(answer, dict): # Handle data that are dictionary instead of plain text
                            # print(f" {section} ---- {answer}")
                            if "value" in answer:
                                if answer["value"] == "Yes": 
                                    section_yes += 1
                                    total_yes += 1

                                    # Apply grading logic
                                    if section in grading_criteria:
                                        
                                        if section =="MAST":
                                            if question_number in ["1","4","6","7"]:
                                                section_score = section_score #do not update since these question will not get a point if they are "yes"
                                            elif question_number in ["23", "24"]: #Special grading formular for these questions  in MAST section
                                                number_of_times = int(answer["additional"]["Number of Times"])
                                                section_score += grading_criteria[section].get(question_number, 0) * number_of_times    
                                            else:
                                                section_score += grading_criteria[section][question_number]
                                        elif section == "S_I": #Handle S_I section grading
                                            section_score = int(question_number)
                                        
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
                                            if section == "MAST":
                                                if question_number in ["1","4","6","7"]:
                                                    section_score += grading_criteria[section][question_number]
                                            '''
                                            else:     
                                                section_score += grading_criteria[section][question_number]
                                            '''
                                        else:
                                            if section =="H_I": # this is because I didn't sepcify the grading for H_I section in its dict
                                                section_score = section_score #Also not updating because this section does not get a point for any "No" answer      
                                            '''
                                            else:
                                                section_score += grading_criteria[section].get("default", 0)
                                            '''
                                    
                            # V_I section does not have "value" field in its data so has to be handled individually                           
                            elif section in [ "V_I", "L_O_F"]:
                                
                                for sub_question, sub_answer in answer.items():
                                    if sub_answer == "Yes":
                                        sub_score = grading_criteria[section].get(question_number, {})
                                        print(f"Grading for {section} -> Question {question_number}: +{grading_criteria[section][question_number]}")
                                        if isinstance(sub_score, dict):
                                            print(f"123456\n")
                                            if question_number != "2" and section == "L_O_F":
                                            
                                                section_score = sub_score.get(sub_question, 0)  # graded with the highest number yes only instead of adding all together, Also we only grade the first part of LOF not the second (i.e Part A and B)
                                            elif section == "V_I":
                                                section_score = sub_score.get(sub_question, 0)

                        # If the answer is a direct string response
                        elif isinstance(answer, str): #Handle data that are plain text instead of dictionary
                            if answer == "Yes": 
                                section_yes += 1
                                total_yes += 1
                                # Apply grading logic
                                if section in grading_criteria:
                                    if section == "MAST":
                                        
                                        if question_number in ["1","4","6","7"]:
                                            
                                            section_score = section_score #do not update since these question will not get a point if they are "yes"
                                        else:
                                            section_score += grading_criteria[section][question_number]
                                    elif section in ["S_I", "V_I", "L_O_F"]:
                                        section_score = int(question_number)
                                    elif section == "D_I":
                                        if question_number in ["6"]:
                                            
                                            section_score = section_score #do not update since these question will not get a point if they are "yes"
                                        else:
                                            section_score += grading_criteria[section][question_number]
                                    elif question_number and question_number in grading_criteria[section]:
                                        section_score += grading_criteria[section][question_number]
                                    
                                    
                                    else:
                                        
                                        section_score += grading_criteria[section].get("default", 0)
                            
                            elif answer == "No":
                                section_no += 1
                                total_no += 1
                                if section=="MAST":
                                    # Apply grading logic
                                    if section in grading_criteria:
                                        if question_number and question_number in grading_criteria[section]:
                                            if question_number in ["1","4","6","7"]:
                                                section_score += grading_criteria[section][question_number]
                                            '''
                                            else:
                                                section_score =section_score #DO not update since other "No" is not counted for points
                                            
                                        else:
                                            section_score += grading_criteria[section].get("default", 0)
                                            '''
                                elif section=="D_I" and question_number in ["6"]: # Only question 6 of D_I can get a point when the answer is no
                                    # Apply grading logic
                                    if section in grading_criteria:
                                        if question_number and question_number in grading_criteria[section]:
                                            section_score += grading_criteria[section][question_number]
                                        else:
                                            section_score += grading_criteria[section].get("default", 0)
                                elif section =="H_I":
                                    section_score = section_score #Also not updating because this section does not get a point for any "No" answer       
                        print(f"section score: {section_score}")   
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

