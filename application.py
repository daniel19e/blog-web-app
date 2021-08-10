from flask import Flask, flash, redirect, render_template, request, session


app = Flask(__name__)

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
