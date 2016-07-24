# -*- coding: utf-8 -*-

from . import api
from datetime import  datetime
from flask import request,jsonify
from ..models import User,Order,Good
from flask_login import current_user,login_required

# 列出作为卖家的订单
# params[POST]:
#   'userID' [int]
#   'start' [int]
#   'count' [int]
#   'status' [int]
# @login_required
@api.route('/list_seller_orders', methods = ['POST'])
def list_seller_orders():
    object = request.json
    userID = object['userID']
    start = object['start']
    stop = start + object['count'] - 1
    status = object['status']
    sellerID = userID
    if not sellerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login'
            }
        )


    try:
        ordersID = Order.query(Order.orderID).filter(sellerID == Order.sellerID and status == Order.status).slice(start,stop)

        if not ordersID:
            return jsonify(

                {
                    'status': 2,
                    'message': 'Fail: No order',
                    'data': {}
                }
            )
    except:
        return jsonify(
            {
                'status' : 3,
                'message': 'Fail: Database Error',
                'data':{}
            }
        )

    try:
        orderlist = list()
        for orderID in ordersID:
            orderinfo = Order.query(Order).filter(orderID == Order.orderID).first()
            orderinfo = dict(orderinfo,**Good.query(Good.goodName).filter(Good.goodID == orderinfo.goodID).first())
            orderinfo = dict(orderinfo,**User.query(User.userName).filter(User.userID == orderinfo.buyerID).first())
            orderlist.append(orderinfo)

        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data' : orderlist
            }
        )
    except:
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )

# 列出作为买家的订单
# params[POST]:
#   'userID' [int]
#   'start' [int]
#   'count' [int]
#   'status' [int]
# @login_required
@api.route('/list_seller_orders', methods = ['POST'])
def list_buyer_orders():
    object = request.json
    userID = object['userID']
    start = object['start']
    stop = start + object['count'] - 1
    status = object['status']
    buyerID = userID
    if not buyerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login'
            }
        )

    try:
        ordersID = Order.query(Order.orderID).filter(buyerID == Order.buyerID and status == Order.status).slice(start,stop)
        if not ordersID:
            return jsonify(
                {
                    'status' : 2,
                    'message' : 'Fail: No order'
                }
            )
    except:
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )

    try:
        orderlist = list()
        for orderID in ordersID:
            orderinfo = Order.query(Order).filter(orderID == Order.orderID).first()
            orderinfo = dict(orderinfo,**Good.query(Good.goodName).filter(Good.goodID == orderinfo.goodID).first())
            orderinfo = dict(orderinfo,**User.query(User.userName).filter(User.userID == orderinfo.sellerID).first())
            orderlist.append(orderinfo)
        return jsonify(
            {
                'status' : 'Success',
                'message' : orderlist
            }
        )
    except:
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )


# 获取订单详情
# params[POST]:
#   'orderID' [int]
# @login_required
@api.route('/get_order_detail', methods = ['POST'])
def get_order_detail():
    object = request.json
    orderID = object['orderID']
    try:
        orderDetail = Order.query(Order).filter(Order.orderID == orderID).first()

        if not orderDetail:
            return jsonify(
                {
                    'status':0,
                    'message':'No Such Order',
                    'Data':{}
                }
            )

        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data' : orderDetail
            }
        )
    except:
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )

# 创建新订单
# params[POST]:
#   'goodID' [int]
#   'buyerID' [int]
#   'sellerID' [int]
#   'count' [int]
# @login_required
@api.route('/create_order',methods = ['POST'])
def create_order():
    neworderinfo = request.json
    timenow = datetime.utcnow()
    if neworderinfo.sellerID == neworderinfo.buyerID:
        return jsonify(
            {
                'status': 2,
                'message': 'Same Seller and Buyer',
                'data': {}
            }
        )
    try:
        neworder = Order(
            goodID = neworderinfo.goodID,
            sellerID = neworderinfo.sellerID,
            buyerID = neworderinfo.buyerID,
            createDate = timenow,
            confirmDate = timenow,
            count = neworderinfo.count,
            status = 0
        )
        Order.add(neworder)

        return jsonify(
            {
                'status': 1,
                'message': 'Success',
                'data':{}
            }
        )

    except:
        return jsonify(
            {
                'status': 3,
                'message': 'Database Error',
                'data':{}
            }
        )

# 确认订单
# param[POST]:
#   'orderID' [int]
# @login_required
@api.route('/confirm_order',methods = ['POST'])
def confirm_order():
    object = request.json
    orderID = object['orderID']
    try:
        currentStatus = Order.query(Order.status).filter(Order.orderID == orderID).first()
        if not currentStatus:
            return (
                {
                    'status':2,
                    'message': 'No Such Order',
                    'data':{}
                }
            )
    except:
        return jsonify(
            {
                'status':3,
                'message':'Database Error',
                'data':{}
            }
        )

    if currentStatus == 0:
        try:
            Order.query(Order).filter(Order.orderID == orderID).update({'status':1})
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{}
                }
            )
        except:
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data':{}
                }
            )
    else:
        return jsonify(
            {
                'status': 0,
                'message': 'Order Has Already Confirmed',
                'data':{}
            }
        )

# 取消订单
# param[POST]:
#   'orderID' [int]
# @login_required
@api.route('/complete_order',methods = ['POST'])
def complete_order():
    orderID = request.form['orderID']
    try:
        currentStatus = Order.query(Order.status).filter(Order.orderID == orderID).first()
        if not currentStatus:
            return (
                {
                    'status':2,
                    'message': 'No Such Order',
                    'data':{}
                }
            )

    except:
        return jsonify(
            {
                'status':3,
                'message':'Database Error',
                'data':{}
            }
        )

    if currentStatus == 0:
        try:
            Order.query(Order).filter(Order.orderID == orderID).update({'status': 1})
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{}
                }
            )
        except:
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data':{}
                }
            )
    else:
        return jsonify(
            {
                'status': 0,
                'message': 'Order Has Already Canceled',
                'data':{}
            }
        )
