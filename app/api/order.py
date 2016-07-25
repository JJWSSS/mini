# -*- coding: utf-8 -*-

from . import api
from .. import db
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
@login_required
@api.route('/list_seller_orders', methods = ['POST'])
def list_seller_orders():
    object = request.json
    # sellerID = object['userID']
    sellerID = current_user.userID
    start = object['start']
    stop = start + object['count'] - 1
    status = object['status']

    if not sellerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login'
            }
        )


    try:
        ordersID = Order.query.filter(sellerID == Order.sellerID, status == Order.status).slice(start,stop).all()

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

    # try:
    orderlist = list()
    print (orderlist)
    for row in ordersID:
        orderID = row.orderID
        orderdetail = Order.query.filter(orderID == Order.orderID).first()
        orderinfo = {
            'orderID' : orderdetail.orderID,
            'goodID': orderdetail.goodID,
            'sellerID': orderdetail.sellerID,
            'buyerID': orderdetail.buyerID,
            'createDate': orderdetail.createDate,
            'confirmDate': orderdetail.confirmDate,
            'count': orderdetail.count,
            'status': orderdetail.status
        }
        print (orderinfo)
        good = Good.query.filter(Good.goodID == orderinfo['goodID']).first()
        orderinfo = dict(orderinfo,**{'goodName':good.goodName})
        user = User.query.filter(User.userID == orderinfo['sellerID']).first()
        orderinfo = dict(orderinfo,**{'userName':user.userName})
        orderlist.append(orderinfo)

    print (orderlist)

    return jsonify(
        {
            'status' : 1,
            'message' : 'Success',
            'data' : orderlist
        }
    )
    '''except:
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )'''

# 列出作为买家的订单
# params[POST]:
#   'userID' [int]
#   'start' [int]
#   'count' [int]
#   'status' [int]
@login_required
@api.route('/list_buyer_orders', methods = ['POST'])
def list_buyer_orders():
    object = request.json
    buyerID = current_user.userID
    start = object['start']
    stop = start + object['count'] - 1
    status = object['status']
    if not buyerID:
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login',
                'data':{}
            }
        )

    try:
        ordersID = Order.query.filter(buyerID == Order.buyerID and status == Order.status).slice(start,stop).all()
        if not ordersID:
            return jsonify(
                {
                    'status' : 2,
                    'message' : 'Fail: No order',
                    'data':{}
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
        for row in ordersID:
            orderID = row.orderID
            orderdetail = Order.query.filter(orderID == Order.orderID).first()
            orderinfo = {
                'orderID': orderdetail.orderID,
                'goodID': orderdetail.goodID,
                'sellerID': orderdetail.sellerID,
                'buyerID': orderdetail.buyerID,
                'createDate': orderdetail.createDate,
                'confirmDate': orderdetail.confirmDate,
                'count': orderdetail.count,
                'status': orderdetail.status
            }
            good = Good.query.filter(Good.goodID == orderinfo['goodID']).first()
            orderinfo = dict(orderinfo,**{'goodName':good.goodName})
            user = User.query.filter(User.userID == orderinfo['buyerID']).first()
            orderinfo = dict(orderinfo,**{'userName':user.userName})
            orderlist.append(orderinfo)
        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data': orderlist
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
    if neworderinfo['sellerID'] == neworderinfo['buyerID']:
        return jsonify(
            {
                'status': 2,
                'message': 'Same Seller and Buyer',
                'data': {}
            }
        )
    try:
        neworder = Order(
            goodID = neworderinfo['goodID'],
            sellerID = neworderinfo['sellerID'],
            buyerID = neworderinfo['buyerID'],
            createDate = timenow,
            confirmDate = timenow,
            count = neworderinfo['count'],
            status = 0
        )
        db.session.add(neworder)
        db.session.commit()

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
# 状态 0：未确认  1：买家单方面确认  2：卖家单方面确认 3：已确
@login_required
@api.route('/confirm_order',methods = ['POST'])
def confirm_order():
    object = request.json
    userID = current_user.userID
    orderID = object['orderID']

    try:
        order = Order.query.filter(Order.orderID == orderID).first()
        if not order:
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

    currentStatus = order.status
    if order.status == 0:
        try:
            if userID == order.buyerID:
                Order.query.filter(Order.orderID == orderID).update({'status':1})
                currentStatus = 1
            elif userID == order.sellerID:
                Order.query.filter(Order.orderID == orderID).update({'status':2})
                currentStatus = 2
            else:
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status':currentStatus }
                    }
                )

            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{'status': currentStatus }
                }
            )

        except:
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data':{'status': currentStatus }
                }
            )

    elif order.status == 1:
        try:
            if userID == order.sellerID:
                Order.query.filter(Order.orderID == orderID).update({'status': 3, 'confirmDate':datetime.utcnow()})
                currentStatus = 3
            elif userID == order.buyerID:
                return jsonify(
                    {
                        'status': 5,
                        'message': 'You Hava Already Confirmed',
                        'data': {'status': currentStatus }
                    }
                )
            else:
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status': currentStatus }
                    }
                )

            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{'status': currentStatus }
                }
            )

        except:
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data': {'status': currentStatus }
                }
            )

    elif order.status == 2:
        try:
            if userID == order.buyerID:
                Order.query.filter(Order.orderID == orderID).update({'status': 3, 'confirmDate':datetime.utcnow()})
                currentStatus = 3
            elif userID == order.sellerID:
                return jsonify(
                    {
                        'status': 5,
                        'message': 'You Hava Already Confirmed',
                        'data': {'status': currentStatus }
                    }
                )
            else:
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status': currentStatus }
                    }
                )

            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data': {'status': currentStatus }
                }
            )

        except:
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data': {'status': currentStatus }
                }
            )
    else:
        if userID == order.buyerID or userID == order.sellerID:
            return jsonify(
                {
                    'status': 5,
                    'message': 'You Hava Already Confirmed',
                    'data': {'status': currentStatus }
                }
            )
        else:
            return jsonify(
                {
                    'status': 4,
                    'message': 'User Is Not Either Buyer Or Seller',
                    'data': {'status': currentStatus }
                }
            )




