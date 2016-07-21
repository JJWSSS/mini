from . import db
from flask_login import UserMixin
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer, primary_key=True, index=True)
    goodID = db.Column(db.Integer, db.ForeignKey('goods.goodID'))
    sellerID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    buyerID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    createDate = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    confirmDate = db.Column(db.DateTime, index=True, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True, index=True)
    userName = db.Column(db.String(64), unique=True, nullable=True, index=True)
    nickName = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    isAuthenticated = db.Column(db.Boolean, nullable=False, default=False)
    qq = db.Column(db.Integer, nullable=True)
    goods = db.relationship('Good', backref='seller', lazy='dynamic')
    sellerOrders = db.relationship('Order', foreign_keys=[Order.sellerID], backref='seller', lazy='dynamic')
    buyerOrders = db.relationship('Order', foreign_keys=[Order.buyerID], backref='buyer', lazy='dynamic')
    comments = db.relationship('Comment', backref='commentator', lazy='dynamic')


class Good(db.Model):
    __tablename__ = 'goods'
    goodID = db.Column(db.Integer, primary_key=True, index=True)
    goodName = db.Column(db.String(128), nullable=False)
    sellerID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    createDate = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    modifyDate = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    status = db.Column(db.Boolean, default=True)
    freeCount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    compressImage = db.Column(db.Text, nullable=False)
    contact = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    orders = db.relationship('Order', backref='good', lazy='dynamic')
    comments = db.relationship('Comment', backref='good', lazy='dynamic')


class Comment(db.Model):
    __tablename__ = 'comments'
    commentID = db.Column(db.Integer, primary_key=True, index=True)
    goodID = db.Column(db.Integer, db.ForeignKey('goods.goodID'))
    commentatorID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    context = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=0)
