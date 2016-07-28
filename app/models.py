
# -*- coding: utf-8 -*-

from . import db, login_manager
from flask_login import UserMixin, AnonymousUserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, url_for
from sqlalchemy import func
from datetime import datetime


class Order(db.Model):
    __tablename__ = 'orders'
    orderID = db.Column(db.Integer, primary_key=True, index=True)
    goodID = db.Column(db.Integer, db.ForeignKey('goods.goodID'), nullable=False)
    sellerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False)
    buyerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False)
    createDate = db.Column(db.DateTime, index=True, nullable=False)
    confirmDate = db.Column(db.DateTime, index=True, nullable=False)
    count = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False) # 订单状态：0：未确认， 1：已确认， 2:已完成


    def get_seller_ordersID(self,sellerID):
        orders = db.session.query(Order).filter(sellerID == Order.sellerID).all()
        return orders

    def get_buyer_ordersID(self,buyerID):
        orders = db.session.query(Order).filter(buyerID == Order.sellerID).all()
        return orders

    def get_order_detail(self,orderID):
        orders = db.session.query(Order).filter(orderID == Order.orderID).first()
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
        return json


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    userID = db.Column(db.Integer, primary_key=True, index=True)
    userName = db.Column(db.String(64), unique=True, nullable=True, index=True)
    nickName = db.Column(db.String(128), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    isAuthenticated = db.Column(db.Integer, nullable=False, default=0)
    qq = db.Column(db.Integer, nullable=True)
    picture = db.Column(db.Text, nullable=True)
    compressPicture = db.Column(db.Text, nullable=True)
    goods = db.relationship('Good', backref='seller', lazy='dynamic')
    sellerOrders = db.relationship('Order', foreign_keys=[Order.sellerID],
                                   backref=db.backref('seller', lazy='joined'), lazy='dynamic',
                                   cascade='all, delete-orphan')
    buyerOrders = db.relationship('Order', foreign_keys=[Order.buyerID],
                                  backref=db.backref('buyer', lazy='joined'), lazy='dynamic',
                                  cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='commentator', lazy='dynamic')


    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_id(self):
        return int(self.userID)


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

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py
        seed()
        for i in range(count):
            u = User(userName=forgery_py.address.phone(), nickName=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(), email=forgery_py.internet.email_address(),
                     isAuthenticated=1, qq=randint(100000000, 999999999))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Good(db.Model):
    __tablename__ = 'goods'
    goodID = db.Column(db.Integer, primary_key=True, index=True)
    goodName = db.Column(db.String(128), nullable=False)
    sellerID = db.Column(db.Integer, db.ForeignKey('users.userID'), nullable=False)
    createDate = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    modifyDate = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    status = db.Column(db.Integer, default=1)
    freeCount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    compressImage = db.Column(db.Text, nullable=False)
    contact_tel = db.Column(db.String(16), nullable=False)
    contact_qq = db.Column(db.Integer, nullable=False)
    contact_wechat = db.Column(db.String(64), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    orders = db.relationship('Order', backref='good', lazy='dynamic')
    comments = db.relationship('Comment', backref='good', lazy='dynamic')
    price = db.Column(db.Float, nullable=False)
    poster = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    times = db.Column(db.Integer, default=0)

    def to_json(self):
        json_post = {
            'goodID': self.goodID,
            'goodName': self.goodName,
            'sellerID': self.sellerID,
            'sellerName': self.seller.nickName,
            'createDate': self.createDate,
            'modifyDate': self.modifyDate,
            'status': self.status,
            'freeCount': self.freeCount,
            'description': self.description,
            'image': self.image,
            'compressImage': self.compressImage,
            'contact_tel': self.contact_tel,
            'contact_qq': self.contact_qq,
            'contact_wechat': self.contact_wechat,
            'type': self.type,
            'price': self.price,
            'poster': self.poster,
            'address': self.address,
            'times': self.times
        }
        return json_post

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            g = Good(goodName=forgery_py.name.full_name(), description=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                     freeCount=10, image=forgery_py.internet.domain_name(), compressImage=forgery_py.internet.domain_name(),
                     contact_tel=randint(100000000, 999999999), type=randint(0, 7), price=randint(1, 100), seller=u,
                     contact_qq=randint(100000000, 999999999), contact_wechat='jjj', address='china', poster='very good')
            db.session.add(g)
            db.session.commit()


class Comment(db.Model):
    __tablename__ = 'comments'
    commentID = db.Column(db.Integer, primary_key=True, index=True)
    goodsID = db.Column(db.Integer, db.ForeignKey('goods.goodID'))
    commentatorID = db.Column(db.Integer, db.ForeignKey('users.userID'))
    context = db.Column(db.String(512), nullable=False)
    status = db.Column(db.Integer, default=0)
    commitTime = db.Column(db.DateTime, default=datetime.utcnow)


"""
class DescOfQurey:
    def __get__(self, instance, owner):
        if hasattr(owner, 'Model'):
            return owner.Model.query
        Model = type('Comment', (db.Model,), current_app.config.get('COMMENT_TABLE_STRUCTS'))
        setattr(owner, 'Model', Model)
        setattr(owner, 'query', Model.query)
        return Model.query


class Comment:
    query = DescOfQurey()

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, 'Model'):
            return cls.Model(*args, **kwargs)

        Model = type('Comment', (db.Model,), current_app.config.get('COMMENT_TABLE_STRUCTS'))
        setattr(cls, 'Model', Model)
        return Model(*args,  **kwargs)
"""


class AnonymousUser(AnonymousUserMixin):
    pass

login_manager.anonymous_user = AnonymousUser

