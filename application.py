from flask import Flask, flash, redirect, render_template, request, session
from functools import wraps
from forms import Register, Login


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vzj9ew5aeuqf5m19'

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

@app.route("/register", methods=['GET','POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        flash(f'Successfully created an account for {form.username.data}', 'info')
        return redirect('/')
    return render_template("register.html", title="Register", form=form)
@app.route("/login")
def login():
    form = Login()
    return render_template("login.html", title = "Login", form=form)

if __name__ == '__main__':
    app.run(debug=True)
