from logging import log
import secrets
from PIL import Image
import os
from flask import flash, redirect, render_template, url_for, request, abort
from application import app, db, bcrypt, mail
from application.models import BlogPost, User
from application.forms import Register, Login, UpdateAccountInfo, Post, RequestReset, PasswordReset
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.date.desc()).paginate(page=page, per_page=4)
    return render_template("home.html", posts=posts)

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

def get_picture(form_pic):
    rand_hex = secrets.token_hex(8)
    _ , file_extension = os.path.splitext(form_pic.filename)
    pict_name = rand_hex + file_extension
    picture_path = os.path.join(app.root_path, 'static/profile_pics', pict_name)
    
    size = (400, 400)
    resized_pic = Image.open(form_pic)
    resized_pic.thumbnail(size)  #changing size of picture to save space
    resized_pic.save(picture_path)  
    #check if previous picture isn't the default picture
    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image)
    if os.path.exists(prev_picture) and current_user.image != 'default.jpg':
        os.remove(prev_picture)
    return pict_name

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountInfo()
    if form.validate_on_submit():
        if form.prof_pic.data:
            picture_file = get_picture(form.prof_pic.data)
            current_user.image = picture_file
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


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = Post()
    if form.validate_on_submit():
        post = BlogPost(title=form.title.data, body=form.body.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully', 'info')
        return redirect('/')
    return render_template('new_post.html', title='New Post', 
                            form=form, legend="New Post")

@app.route('/post/<int:post_id>')
def post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = Post()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash("Post updated successfully", 'info')
        return redirect('/')
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    return render_template('new_post.html', title='Update Post', 
                            form=form, legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully', 'info')
    return redirect('/')

@app.route("/user/<string:username>")
def post_by_user(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = BlogPost.query.filter_by(author=user)\
        .order_by(BlogPost.date.desc())\
        .paginate(page=page, per_page=4)
    return render_template("post_by_user.html", posts=posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                    sender='noreply@demo.com', 
                    recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token',token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made'''

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect('/')
    form = RequestReset()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect('/login')
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect('/')
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = PasswordReset()
    if form.validate_on_submit():
        hash_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hash_pw
        db.session.commit()
        flash('Your password has been updated', 'info')
        return redirect('/login')
    return render_template('reset_token.html', title='Reset Password', form=form)
