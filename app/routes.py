from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User, Character, Article
from flask_login import logout_user
from flask_login import login_required
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import UserRegistrationForm
from datetime import datetime
from app.forms import EditProfileForm
from app.forms import ArticleForm
from app.forms import EmptyForm


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ArticleForm()
    if form.validate_on_submit():
        article = Article(headline=form.headline.data, body=form.body.data, author=current_user)
        db.session.add(article)
        db.session.commit()
        flash('Your article is now live.')
        return redirect(url_for('index'))
    articles = Article.query.all()
    chars = Character.query.all()
    return render_template('index.html', title='Articles', articles=articles, form=form, chars=chars)

@app.route('/knowledge')
@login_required 
def knowledge():
    return render_template('knowledge.html', title='Knowledge')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    my_team = current_user.team_characters().all()
    form = EmptyForm()
    return render_template('user.html', user=user, my_team=my_team, form=form)

@app.route('/login', methods={'GET', 'POST'})
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserRegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        char = Character(name=form.name.data, player=user)
        db.session.add(char)
        db.session.commit()
        flash('Congratulations, you are now a registered.')
        return redirect(url_for('login'))       
    return render_template('register_user.html', title='User Registration', form=form)

from app.forms import EditProfileForm

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(
        current_user.username,
        current_user.my_character().name,
        current_user.my_character().level,
        current_user.my_character().speed,
        )
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.my_character().name = form.char_name.data
        current_user.my_character().level = form.char_level.data
        current_user.my_character().speed = form.char_speed.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.char_name.data = current_user.my_character().name
        form.char_level.data = current_user.my_character().level
        form.char_speed.data = current_user.my_character().speed
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/join_user/<username>', methods=['POST'])
@login_required
def join_user(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for('index'))
        if user == current_user:
            flash(f"You cannot team up with yourself.")
            return redirect(url_for('user', username=username))
        current_user.join_team(user)
        db.session.commit()
        flash(f'You have requested to team up with {username}.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

@app.route('/leave_user/<username>', methods=['POST'])
@login_required
def leave_user(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(f"User {username} not found.")
            return redirect(url_for('index'))
        if user == current_user:
            flash(f"You cannot leave yourself behind.")
            return redirect(url_for('user', username=username))
        current_user.leave_team(user)
        user.leave_team(current_user)
        db.session.commit()
        flash(f'You have left the team.')
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
