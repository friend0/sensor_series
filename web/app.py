"""

Entry for the docker container running the Flask app.

"""

import os
from flask import Flask
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from web import config
from flask import request, redirect, render_template, url_for, flash
from flask_login import login_user, logout_user, login_required
from web.forms import LoginForm
from web.user import User
import pymongo
import json
from bson import json_util
from bson.json_util import dumps

app = Flask(__name__)

mongo_host = os.environ.get('MONGO_PORT_27017_TCP_ADDR') or 'localhost'
mongo_port = 27017
app.config["SECRET_KEY"] = "my_precious"
app.config['WTF_CSRF_ENABLED'] = True
app.config['MONGODB_SETTINGS'] = {
    'db': 'biw',
    'host': mongo_host,
    'port': 27017
}

#client = MongoClient(mongo_host, 27017, connect=False)
#db = client.tododb
db = MongoEngine(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'


# Controller

@app.route("/controller/get_robots")
def get_robots():
    connection = pymongo.MongoClient(host='10.0.2.2')
    collection = connection['robots']['robot_map']
    projects = collection.find(projection= {'_id':0})
    json_projects = []
    for project in projects:
        print(project)
        json_projects.append(project)
    json_projects = dumps(json_projects, default=json_util.default)
    connection.close()
    return json_projects

# View
from web import models, views
@app.route('/', methods=['GET'])
def home():
    #_items = db
    #items = [item for item in _items]
    # return render_template('/base.html')
    return render_template('/home.html')

@app.route('/index')
def index():
    _items = db
    #items = [item for item in _items]
    # return render_template('./templates/base.html')
    return render_template('/index.html')

@app.route('/new', methods=['POST'])
def new():

    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    app.db.tododb.insert_one(item_doc)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')