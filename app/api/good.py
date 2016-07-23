# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify, g, current_app
from ..models import User, Good
from .. import db
from .errors import forbidden
from werkzeug.utils import secure_filename
import os
from PIL import Image


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@api.route('/goods/', methods=['POST'])
def get_goods():
    # 验证文件编码
    userid = request.form['userID']
    user = User.query.get_or_404(userid)
    return jsonify({'goods': [good.to_json() for good in user.goods]})


@api.route('/good/<int:good_id>')
def single_good(good_id):
    good = Good.query.get_or_404(good_id)
    return jsonify(good.to_json())


@api.route('/search/', methods=['POST'])
def search():
    search_name = request.form['search_name']
    goods = Good.query.filter_by(Good.goodName.find(search_name) != -1).all()
    result_code = 0
    if goods:
        result_code = 1
    return jsonify({'result': [good.to_json() for good in goods], 'result_code': result_code})


@api.route('/new_good/', methods=['POST'])
def new_good():
    good = Good(goodName=request.form['goodName'], description=request.form['description'],
                status=request.form['status'], freecount=request.form['freeCount'], type=request.form['type'],
                contact=request.form['contact'])
    file = request.files['file']
    if file and allowed_file(file.filename):
        im = Image.open(file)
        filename = secure_filename(file.filename)
        url = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        im.save(url)
        im.thumbnail((40, 40))
        compress_url = os.path.join(current_app.config['UPLOAD_FOLDER'], ('compress_' + filename))
        im.save(compress_url)
        good.image = url
        good.compressImage = compress_url
    good.seller = g.current_user
    db.session.add(good)
    db.session.commit()
    return jsonify(good.to_json()), 201


@api.route('/edit_good/<int:good_id>', methods=['PUT'])
def edit_good(good_id):
    good = Good.query.get_or_404(good_id)
    if g.current_user != good.seller:
        return forbidden('Insufficient permissions')
    good.description = request.form['description']
    db.session.add(good)
    return jsonify(good.to_json())


@api.route('/delete_good/<int:good_id>', methods=['DELETE'])
def delete_good(good_id):
    good = Good.query.get_or_404(good_id)
    db.session.delete(good)
    return jsonify({'result_code': 1})
