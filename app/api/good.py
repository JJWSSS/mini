# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify
from ..models import User, Good


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
    pass
