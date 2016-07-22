# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify
from ..models import User, Good


@api.route('/goods', methods=['POST'])
def get_goods():
    # 验证文件编码
    userid = request.form['userID']
    user = User.query.get_or_404(userid)
    return jsonify({'goods': [good.to_json() for good in user.goods]})


@api.route('/good/<int:id>')
def single_good(id):
    pass