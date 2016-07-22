# -*- coding: utf-8 -*-

from . import api
from flask import request,jsonify
from ..models import User,Order

@api.route('/listorders/<int:userid>', methods=['POST','get'])
def list_orders(request):
    userID = request.Form['userID']
    user = User.query.get_or_404(userID)
    return jsonify({'orders': [Order.to_json() for ]})
