import os
from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from flask_mongoengine import MongoEngine

mongo_host = os.environ.get('MONGO_PORT_27017_TCP_ADDR') or 'localhost'
mongo_port = 27017

#client = MongoClient(mongo_host, 27017, connect=False)
#db = client.tododb

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

app = Flask(__name__, template_folder='templates')

app.config["SECRET_KEY"] = "my_precious"
app.config['WTF_CSRF_ENABLED'] = True

app.config['MONGODB_SETTINGS'] = {
    'db': 'robots',
    'host': mongo_host,
    'port': 27017
}

db = MongoEngine(app)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

from web import models, views
