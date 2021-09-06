from logging import log
from flask import flash, redirect, render_template, url_for, request
from application import app, db, bcrypt
from application.models import User
from application.forms import Register, Login, UpdateAccountInfo
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html", title = "About")

@app.route("/register", methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect('/')
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
    if current_user.is_authenticated:
        return redirect('/')
    form = Login()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_user.data)
            return redirect('/')
        else:
            flash('Incorrect Email or Password', 'danger')
    return render_template("login.html", title = "Login", form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountInfo()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully', 'info')
        return redirect('/account')
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    img_file = url_for('static', filename='profile_pics/' + current_user.image)
    return render_template('account.html', title='Account',
                            img_file=img_file, form=form)
