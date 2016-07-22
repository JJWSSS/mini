# -*- coding: utf-8 -*-

import os
from app import db

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

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://jjw:101023@localhost/mini'


class CommentTestConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:lee@localhost/TEST'
    COMMENT_GET_URL = '/comment/get'
    COMMENT_ADD_URL = '/comment/insert'
    COMMENT_TABLE_STRUCTS = {'__tablename__': 'comments',
                             'commentID': db.Column(db.Integer, primary_key=True, index=True) ,
                             'goodsID': db.Column(db.Integer, db.ForeignKey('goods.goodID')),
                             'commentatorID': db.Column(db.Integer, db.ForeignKey('users.userID')),
                             'context': db.Column(db.String(512), nullable=False),
                             'status': db.Column(db.Integer, default=0),
                             }


config = {'default': DevelopmentConfig, 'comment':CommentTestConfig}
