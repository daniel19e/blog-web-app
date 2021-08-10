from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps


app = Flask(__name__)

def login_required(f):
    """
    Decorate routes to require login.
    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html", title = "About")

@app.route("/register")
def register():
    return render_template("register.html", title= "Register")

@app.route("/login")
def login():
    return render_template("login.html", title = "Login")

if __name__ == '__main__':
    app.run(debug=True)
