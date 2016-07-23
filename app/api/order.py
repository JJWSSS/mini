# -*- coding: utf-8 -*-

from . import api
from flask import request,jsonify
from ..models import User,Order,Good
from flask_login import current_user,login_required

# 列出作为卖家的订单
# params[POST]:
#   'start' [int]
#   'count' [int]
@login_required
@api.route('/list_seller_orders', method = ['POST'])
def list_seller_orders():
    requestinfo = request.json
    start = requestinfo.start
    stop = start + requestinfo.count - 1
    sellerID = current_user.userID
    if not sellerID:
        return jsonify(
            {
                'status' : 'Fail',
                'message' : 'User Not Login'
            }
        )
    ordersID = Order.query(Order.orderID).filter(sellerID == Order.sellerID).slice(start,stop)
    orderlist = list()
    for orderID in ordersID:
        orderinfo = Order.query(Order).filter(orderID == Order.orderID).first()
        orderinfo = dict(orderinfo,**Good.query(Good.goodName).filter(Good.goodID == orderinfo.goodID).first())
        orderinfo = dict(orderinfo,**User.query(User.userName).filter(User.userID == orderinfo.buyerID).first())
        orderlist.append(orderinfo)
    return jsonify()


# 列出作为买家的订单
@api.route('/list_seller_orders', method = ['POST'])
def list_buyer_orders():
    buyerID = current_user.userID
    orders = Order.get_buyer_orders(buyerID)
    return orders

# 获取订单详情
@api.route('/get_order_detail', method = ['POST'])
def get_order_detail()
    requeseInfo = request.json
    orderID = requeseInfo['orderID']
    order = Order.get_order_detail(orderID)
    return order

