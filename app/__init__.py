from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config

mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
LoginManager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app()
    mail.init_app()
    login_manager.init_app()

    return app
