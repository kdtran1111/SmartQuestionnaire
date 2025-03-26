from Routes.init import create_app
from Routes.index import init_index_routes
from Routes.questionnaire import init_questionnaire_routes
from Routes.questionnaire_start import init_questionnaire_start_routes
from Routes.questionnaire_display import init_questionnaire_display_routes
from Routes.questionnaire_continue import init_questionnaire_continue_routes
from Routes.debug import init_debug_routes
from sympy import content
from bson import ObjectId
from website import create_app
from website.database import db, responsesCol, questionnaireCol, usersCol  # Import database collections
from flask import flash, render_template, request, redirect, url_for, session 
from flask_login import UserMixin
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from website.database import usersCol

app = create_app()

# Initialize all routes
# These functions are defined in the Routes folder.
#  Therefore, 
# make changes in those files instead

init_index_routes(app)
init_questionnaire_routes(app)
init_questionnaire_start_routes(app)
init_questionnaire_display_routes(app)
init_questionnaire_continue_routes(app)
init_debug_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
