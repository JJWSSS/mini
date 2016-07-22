# -*- coding: utf-8 -*-

from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for


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

    def get_seller_orders(self,sellerID):
        orders = db.session.query(Order).filter(sellerID == Order.sellerID).all()
        return orders

    def get_buyer_orders(self,buyerID):
        orders = db.session.query(Order).filter(buyerID == Order.sellerID).all()
        return orders

    def get_order_detail(self,orderID):
        orders = db.session.query(Order).filter(orderID == Order.orderID).one()
        return orders

    def to_json(self):
        json = {
            'orderID': self.orderID,
            'goodID': self.goodID,
            'sellerID': self.sellerID,
            'buyerID': self.buyerID,
            'createDate': self.createDate,
            'confirmDate': self.confirmDate,
            'count': self.count,
            'status': self.status
        }


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

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.isAuthenticated = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

    def to_json(self):
        json_post = {
            'goodID': self.goodID,
            'url': url_for('api.single_good', good_id=self.goodID, _external=True),
            'goodName': self.goodName,
            'sellerID': self.sellerID,
            'freeCount': self.freeCount,
            'description': self.description,
            'image': self.image,
            'compressImage': self.compressImage,
            'contact': self.contact,

            'comments': url_for('api.get_comments', id=self.goodID,
                                _external=True),
        }
        return json_post


class Comment(db.Model):
    __tablename__ = 'comments'
    commentID = db.Column(db.Integer, primary_key=True, index=True)
    goodID = db.Column(db.Integer, db.ForeignKey('goods.goodID'))
    commentatorID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    context = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=0)


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser
