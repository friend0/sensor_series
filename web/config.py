import os

ENV = os.environ.get('ENVIRONMENT', 'dev')
SECRET_KEY = os.environ.get('SECRET_KEY')

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
ROOT_PATH = BASE_DIR = os.path.join(os.path.dirname(__file__), '..')
TEMPLATE_FOLDER = os.path.join(ROOT_PATH, 'templates')
STATIC_FOLDER = os.path.join(ROOT_PATH, 'static')

CSRF_ENABLED = True