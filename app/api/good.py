# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify, g, current_app
from ..models import User, Good
from .. import db
from werkzeug.utils import secure_filename
import os
from PIL import Image
from datetime import datetime
from random import randint
from flask_login import login_required, current_user


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@api.route('/goods/', methods=['POST'])
@login_required
def get_goods():
    objects = request.json
    userid = objects['userID']
    type = objects['type']
    begin = objects['begin']
    limit = objects['limit']
    if userid:
        if type:
            if begin or limit:
                goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).all()
        elif begin or limit:
            goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).all()
    elif type:
        if begin or limit:
            goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).all()
    else:
        goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
    if goods:
        return jsonify({'error_code': 0, 'goods': [good.to_json() for good in goods]})
    else:
        return jsonify({'error_code': 1, 'goods': None})


@api.route('/good/', methods=['POST'])
@login_required
def single_good():
    objects = request.json
    good = Good.query.get_or_404(objects['good_id'])
    return jsonify(good.to_json())


@api.route('/search/', methods=['POST'])
@login_required
def search():
    search_name = request.json['search_name']
    goods = Good.query.filter(Good.goodName.ilike('%'+search_name+'%')).all()
    result_code = 0
    if goods:
        result_code = 1
        return jsonify({'result_code': result_code, 'result': [good.to_json() for good in goods]})
    else:
        return jsonify({'result_code': result_code, 'result': []})


@api.route('/new_good/', methods=['POST'])
@login_required
def new_good():
    objects = request.json
    good = Good(goodName=objects['goodName'], description=objects['description'],
                freeCount=objects['freeCount'], type=objects['type'],
                contact_tel=objects['contact_tel'], price=objects['price'], contact_qq=objects['contact_qq'],
                contact_wechat=objects['contact_wechat'], image=objects['image_url'],
                compressImage=objects['compress_url'])
    good.seller = current_user
    db.session.add(good)
    db.session.commit()
    return jsonify(good.to_json())


@api.route('/new_photo/', methods=['POST'])
@login_required
def new_photo():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            url = os.path.join(current_app.config['UPLOAD_FOLDER'], (str(randint(1, 100))+filename))
            file.save(url)
            im = Image.open(url)
            im.thumbnail((200, 200))
            compress_url = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                        ('compress_'+str(randint(1, 100))+filename))
            im.save(compress_url)
            return jsonify({'result_code': 1, 'image': url, 'compress_image': compress_url})
        return jsonify({'result_code': 1, 'image': '', 'compress_image': ''})
    except:
        return jsonify({'result_code': 0})


@api.route('/edit_good/', methods=['POST'])
@login_required
def edit_good():
    objects = request.json
    good = Good.query.get_or_404(objects['good_id'])
    good.description = objects['description']
    good.goodName = objects['goodName']
    good.modifyDate = datetime.utcnow()
    good.status = objects['status']
    good.freeCount = objects['freeCount']
    good.contact_tel = objects['contact_tel']
    good.contact_qq = objects['contact_qq']
    good.contact_wechat = objects['contact_wechat']
    good.type = objects['type']
    good.price = objects['price']
    db.session.add(good)
    return jsonify(good.to_json())


@api.route('/delete_good/', methods=['POST'])
@login_required
def delete_good():
    good = Good.query.get_or_404(request.json['good_id'])
    db.session.delete(good)
    return jsonify({'result_code': 1})


@api.route('/homepage_goods/', methods=['POST'])
@login_required
def homepage_goods():
    objects = request.json
    goods = Good.query.filter_by(type=objects['type']).order_by(Good.createDate.desc()).limit(objects['limit']).all()
    if goods:
        return jsonify({'result_code': 1, 'data': [good.to_json() for good in goods]})
    return jsonify({'result_code': 0, 'data': []})


@api.route('/refresh_goods/', methods=['POST'])
@login_required
def refresh_goods():
    objects = request.json
    userid = objects['userID']
    type = objects['type']
    begin = objects['begin']
    limit = objects['limit']
    day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
    if userid:
        if type:
            if begin or limit:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).all()
        elif begin or limit:
            goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).all()
    elif type:
        if begin or limit:
            goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).all()
    else:
        goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
    if goods:
        return jsonify({'error_code': 0, 'goods': [good.to_json() for good in goods]})
    else:
        return jsonify({'error_code': 1, 'goods': None})


@api.route('/more_goods/', methods=['POST'])
@login_required
def more_goods():
    objects = request.json
    userid = objects['userID']
    type = objects['type']
    begin = objects['begin']
    limit = objects['limit']
    day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
    if userid:
        if type:
            if begin or limit:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).all()
        elif begin or limit:
            goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).all()
    elif type:
        if begin or limit:
            goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).all()
    else:
        goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
    if goods:
        return jsonify({'error_code': 0, 'goods': [good.to_json() for good in goods]})
    else:
        return jsonify({'error_code': 1, 'goods': None})


