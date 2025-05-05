from flask import session
from flask_login import current_user
 

# Just a debug route that could be modify to handle more debug cases
def init_debug_routes(app):
    @app.route('/debug')
    def debug():
        if current_user.is_authenticated:
            return f"Logged in as: {current_user.username} (ID: {current_user.id}) Access: {current_user.access}"
        return "Not logged in."

    @app.route('/debug-session')
    def debug_session():
        return str(session)

    # CLI command for listing routes (this can be in a separate utility file if preferred)
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
