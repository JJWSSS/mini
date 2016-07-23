# -*- coding: utf-8 -*-

from . import api
from flask import request,jsonify
from ..models import User,Order

# 列出作为卖家的订单
@api.route('/listsellerorders/<int:sellerID>')
def list_seller_orders(sellerID):
    orders = Order.get_seller_orders(sellerID)
    return orders


# 列出作为买家的订单
@api.route('/listsellerorders/<int:buyerID>')
def list_buyer_orders(buyerID):
    orders = Order.get_buyer_orders(buyerID)
    return orders


# 获取订单详情
@api.route('/getorderdetail/<int:orderID>')
def get_order_detail(orderID):
    order = Order.get_order_detail(orderID)
    return order

