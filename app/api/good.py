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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@api.route('/goods/', methods=['POST'])
def get_goods():
    objects = request.json
    userid = objects['userID']
    type = objects['type']
    begin = objects['begin']
    limit = objects['limit']
    if userid:
        if type:
            if begin or limit:
                goods = Good.query.filter_by(sellerID=userid, type=type).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(sellerID=userid, type=type).all()
        elif begin or limit:
            goods = Good.query.filter_by(sellerID=userid).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter_by(sellerID=userid).all()
    elif type:
        if begin or limit:
            goods = Good.query.filter_by(type=type).offset(begin).limit(limit).all()
        else:
            goods = Good.query.filter_by(type=type).all()
    else:
        goods = Good.query.offset(begin).limit(limit).all()
    if goods:
        return jsonify({'error_code': 0, 'goods': [good.to_json() for good in goods]})
    else:
        return jsonify({'error_code': 1, 'goods': None})


@api.route('/good/<int:good_id>')
def single_good(good_id):
    good = Good.query.get_or_404(good_id)
    return jsonify(good.to_json())


@api.route('/search/', methods=['POST'])
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
def new_good():
    objects = request.json
    good = Good(goodName=objects['goodName'], description=objects['description'],
                freeCount=objects['freeCount'], type=objects['type'],
                contact=objects['contact'], price=objects['price'])
    file = request.files['file']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        url = os.path.join(current_app.config['UPLOAD_FOLDER'], (filename+str(objects['sellerID']+randint(1, 100))))
        file.save(url)
        im = Image.open(url)
        im.thumbnail((200, 200))
        compress_url = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                    ('compress_'+filename+str(objects['sellerID']+randint(1, 100))))
        im.save(compress_url)
        good.image = url
        good.compressImage = compress_url
    good.seller = User.query.get_or_404(objects['sellerID'])
    db.session.add(good)
    db.session.commit()
    return jsonify(good.to_json())


@api.route('/edit_good/<int:good_id>', methods=['POST'])
def edit_good(good_id):
    objects = request.json
    good = Good.query.get_or_404(good_id)
    good.description = objects['description']
    good.goodName = objects['goodName']
    good.modifyDate = datetime.utcnow()
    good.status = objects['status']
    good.freeCount = objects['freeCount']
    good.contact = objects['contact']
    good.type = objects['type']
    good.price = objects['price']
    db.session.add(good)
    return jsonify(good.to_json())


@api.route('/delete_good/<int:good_id>', methods=['GET'])
def delete_good(good_id):
    good = Good.query.get_or_404(good_id)
    db.session.delete(good)
    return jsonify({'result_code': 1})
