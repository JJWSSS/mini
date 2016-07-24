# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
import logging
from os import environ, getcwd, mkdir
from os.path import exists, join
from datetime import datetime

mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
LoginManager.login_view = 'api.login'


# 初始化日志路径以及格式
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
# 通过设置环境变量来设置日志的等级
# $ export LOGGER_LEVEL=0
# 0 For DEBUG, 1 For INFO, 2 For WARNING, 3 For ERROR, 4 For CRITICAL


def create_app(config_name):
    from config import config
    # logger Init
    LEVEL = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL)
    log_level = environ.get('LOGGER_LEVEL')
    if log_level is None:
        log_level = logging.DEBUG
    else :
        log_level = LEVEL[log_level]
    init_logger(log_level=log_level)
    #logging.log(logging.WARNING, "Nothing")

    # app Init
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # buleprint Init
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
