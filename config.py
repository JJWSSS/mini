# -*- coding: utf-8 -*-

import os


class Config:
    SECRET_KEY = 'mini'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_SENDER = ''
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    UPLOAD_FOLDER = '/Users/JJW/Code/mini/photos'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jjw:101023@localhost/mini'


config = {'default': DevelopmentConfig}
