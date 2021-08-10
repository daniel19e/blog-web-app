from flask import Flask, flash, redirect, render_template, request, session


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html", title = "About")

if __name__ == '__main__':
    app.run(debug=True)
