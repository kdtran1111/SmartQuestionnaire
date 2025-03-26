from Routes.init import create_app
from Routes.index import init_index_routes
from Routes.questionnaire import init_questionnaire_routes
from Routes.questionnaire_start import init_questionnaire_start_routes
from Routes.questionnaire_display import init_questionnaire_display_routes
from Routes.questionnaire_continue import init_questionnaire_continue_routes
from Routes.debug import init_debug_routes

app = create_app()

# Initialize all routes
init_index_routes(app)
init_questionnaire_routes(app)
init_questionnaire_start_routes(app)
init_questionnaire_display_routes(app)
init_questionnaire_continue_routes(app)
init_debug_routes(app)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
