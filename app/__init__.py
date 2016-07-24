# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from config import config
import logging
from os import environ, getcwd, mkdir
from os.path import exists, join
from datetime import datetime

mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
LoginManager.login_view = 'api.login'


def init_logger(log_level):
    local_cwd = getcwd()
    tmp = join(local_cwd, 'logs')
    if not exists(tmp):
        mkdir(tmp)
    name_day = str(datetime.now())[:10]
    _log = join(local_cwd, join('logs', 'xiane_log_{}.log'.format(name_day)))
    if not exists(_log):
        with open(_log, 'w') as f:
            pass
    logging.basicConfig(filename=_log, level=log_level,
                        format='[%(levelname)s](%(asctime)s) in %(filename)s:line %(lineno)d : %(message)s')
# 有毒


def create_app(config_name):
    # logger Init
    log_level = environ.get('LOGGER_LEVEL')
    if log_level is None:
        log_level = logging.WARNING
    init_logger(log_level=log_level)
    logging.log(logging.WARNING, "Nothing")

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
