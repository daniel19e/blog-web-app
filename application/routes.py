from flask import flash, redirect, render_template
from application import app, db, bcrypt
from application.models import User
from application.forms import Register, Login

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
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hash_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Successfully created an account for {form.username.data}', 'info')
        return redirect('/login')
    return render_template("register.html", title="Register", form=form)
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        if form.email.data == 'a@gmail.com' and form.password.data == '123':
            flash('Successfully logged in', 'info')
            return redirect('/')
        else:
            flash('Incorrect Username or Password', 'danger')
    return render_template("login.html", title = "Login", form=form)