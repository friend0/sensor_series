from web import app, lm, db
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from .forms import LoginForm
from .user import User


@app.route('/')
def home():
    #_items = db.tododb.find()
    #items = [item for item in _items]
    return "Fuck Off"
    return render_template('base.html')

@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)
    return redirect(url_for('todo'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST' and form.validate_on_submit():
        user = app.config['USERS_COLLECTION'].find_one({"_id": form.username.data})
        if user and User.validate_login(user['password'], form.password.data):
            user_obj = User(user['_id'])
            login_user(user_obj)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("write"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html', title='login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/write', methods=['GET', 'POST'])
@login_required
def write():
    return render_template('write.html')


@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    return render_template('settings.html')


@lm.user_loader
def load_user(username):
    u = app.config['USERS_COLLECTION'].find_one({"_id": username})
    if not u:
        return None
    return User(u['_id'])
