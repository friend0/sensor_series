import os
from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from panopticon import *



tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder='templates')
#app = Flask(__name__)

app.config["SECRET_KEY"] = "my_precious"
app.config['WTF_CSRF_ENABLED'] = True

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

mongo_host = os.environ.get('MONGO_PORT_27017_TCP_ADDR') or 'localhost'
client = MongoClient(mongo_host, 27017)
db = client.tododb

# Do panopticon setup based on Robots in db (will need to persist state about active subscriptions?)
#watch()
#listen()
#learn()

from web import views
