from flask import render_template, redirect, url_for
from flask_login import login_required, current_user
from website.database import responsesCol

def init_questionnaire_start_routes(app):
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