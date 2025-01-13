
# this file defines routes and their logic currently only handles mapping the '/' route to our index html which is what we use as the home page
from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html")