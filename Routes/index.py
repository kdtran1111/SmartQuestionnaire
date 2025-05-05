from flask import render_template
from website.database import questionnaireCol

# This is just a home page route
def init_index_routes(app):
    @app.route('/')
    def index():
        questionnaire_data = list(questionnaireCol.find({}))
        title = questionnaire_data[0].get("Title") if questionnaire_data else "No Title Available"
        return render_template('index.html', title=title)
