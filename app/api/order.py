<<<<<<< HEAD
=======
# -*- coding: utf-8 -*-

from . import api
from datetime import  datetime
from flask import request,jsonify
from ..models import User,Order,Good
from flask_login import current_user,login_required

# 列出作为卖家的订单
# params[POST]:
#   'start' [int]
#   'count' [int]
@login_required
@api.route('/list_seller_orders', methods = ['POST'])
def list_seller_orders():
    start = request.form['start']
    stop = start + request.form['count'] - 1
    status = request.form['status']
    sellerID = current_user.userID
    if not sellerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login'
            }
        )

    ordersID = Order.query(Order.orderID).filter(sellerID == Order.sellerID and status == Order.status).slice(start,stop)
    if not ordersID:
        return jsonify(
            {
                'status' : 2,
                'message' : 'Fail: No order'
            }
        )

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


# 列出作为买家的订单
# params[POST]:
#   'start' [int]
#   'count' [int]
@api.route('/list_seller_orders', methods = ['POST'])
def list_buyer_orders():
    start = request.form['start']
    stop = start + request.form['count'] - 1
    status = request.form['status']
    buyerID = current_user.userID
    if not buyerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login'
            }
        )

    ordersID = Order.query(Order.orderID).filter(buyerID == Order.buyerID and status == Order.status).slice(start,stop)
    if not ordersID:
        return jsonify(
            {
                'status' : 2,
                'message' : 'Fail: No order'
            }
        )

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


# 获取订单详情
# params[POST]:
#   'orderID' [int]
@login_required
@api.route('/get_order_detail', methods = ['POST'])
def get_order_detail():
    orderID = request.form['orderID']
    orderDetail = Order.query(Order).filter(Order.orderID == orderID).first()
    return jsonify(
        {
            'status' : 1,
            'message' : 'Success',
            'data' : orderDetail
        }
    )

# 创建新订单
# params[POST]:
#   'goodID' [int]
#   'buyerID' [int]
#   'sellerID' [int]
#   'count' [int]
@login_required
@api.route('/create_order',methods = ['POST'])
def create_order():
    neworderinfo = request.json
    timenow = datetime.utcnow()
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
            }
        )

    except:
        return jsonify(
            {
                'status': 0,
                'message': 'Database Error',
            }
        )

# 确认订单
# param[POST]:
#   'orderID' [int]
@login_required
@api.route('/confirm_order',methods = ['POST'])
def confirm_order():
    orderID = request.form['orderID']
    currentStatus = Order.query(Order.status).filter(Order.orderID == orderID).first()

    if currentStatus == 1:
        return jsonify(
            {
                'status': 0,
                'message': 'Order Has Already Confirmed'
            }
        )
    elif currentStatus == 2:
        return  jsonify(
            {
                'status': 0,
                'message': 'Order Has Already Complete'
            }
        )
    else:
        try:
            Order.query(Order).filter(Order.orderID == orderID).update({'status':1})
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success'
                }
            )
        except:
            return jsonify(
                {
                    'status': 0,
                    'message': 'Datebase Error'
                }
            )

# 取消订单
# param[POST]:
#   'orderID' [int]
@login_required
@api.route('/complete_order',methods = ['POST'])
def complete_order():
    orderID = request.form['orderID']
    currentStatus = Order.query(Order.status).filter(Order.orderID == orderID).first()

    if currentStatus == 0:
        return jsonify(
            {
                'status': 0,
                'message': 'Order Has not Complete'
            }
        )
    elif currentStatus == 2:
        return jsonify(
            {
                'status': 0,
                'message': 'Order Has Already Canceled'
            }
        )
    else:
        try:
            Order.query(Order).filter(Order.orderID == orderID).update({'status': 2})
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success'
                }
            )
        except:
            return jsonify(
                {
                    'status': 0,
                    'message': 'Datebase Error'
                }
            )

>>>>>>> origin/master
