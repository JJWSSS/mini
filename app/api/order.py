# -*- coding: utf-8 -*-

from . import api
from .. import db
from datetime import  datetime
from flask import request,jsonify
from ..models import User,Order,Good
from flask_login import current_user,login_required
import logging
from sqlalchemy import and_,or_


@login_required
@api.route('/list_seller_orders', methods = ['POST'])
def list_seller_orders():
    '''
    列出作为卖家的订单
    :param:     [JSON]
        "start"
        "count"
        "status"
    :return:    [JSON]
        "status":  0, 1, 2, 3
        "message":
        "data": {}
    '''
    object = request.json
    # sellerID = object['userID']
    sellerID = current_user.userID
    begin = object['begin']
    limit = object['limit']
    status = object['status']

    if not sellerID:
        logging.log(logging.INFO, "Get Orderlist Fail(Not Login): {}".format(current_user.userName))
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login',
                'data':{'orders':{}}
            }
        )


    try:
        if status == 4:
            ordersID = Order.query.filter(sellerID == Order.sellerID).offset(begin).limit(limit).all()
        elif status == 5:
            ordersID = Order.query.filter(or_(Order.sellerID == sellerID,Order.buyerID == sellerID)).offset(begin).limit(limit).all()
        elif status == 6:
            ordersID = Order.query.filter(and_(or_(Order.status == 0,Order.status == 1,Order.status == 2),or_(Order.sellerID == sellerID,Order.buyerID == sellerID))).slice(start, stop).all()
        elif status == 7:
            ordersID = Order.query.filter(and_(Order.status == 3, or_(Order.sellerID == sellerID,Order.buyerID == sellerID))).offset(begin).limit(limit).all()
        else:
            ordersID = Order.query.filter(sellerID == Order.sellerID, status == Order.status).offset(begin).limit(limit).all()

        print(Order.query.filter(Order.sellerID == 2).count())

        if not ordersID:
            logging.log(logging.INFO, "Get Orderlist Fail(No Order): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 2,
                    'message': 'Fail: No order',
                    'data':{'orders':{}}
                }
            )
    except:
        logging.log(logging.INFO, "Get Orderlist Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status' : 3,
                'message': 'Fail: Database Error',
                'data':{'orders':{}}
            }
        )

    try:
        orderlist = list()
        for row in ordersID:
            orderID = row.orderID
            orderdetail = Order.query.filter(orderID == Order.orderID).first()
            orderinfo = {
                'orderID' : orderdetail.orderID,
                'good_id': orderdetail.goodID,
                'sellerID': orderdetail.sellerID,
                'buyerID': orderdetail.buyerID,
                'createDate': orderdetail.createDate,
                'confirmDate': orderdetail.confirmDate,
                'count': orderdetail.count,
                'status': orderdetail.status
            }
            good = Good.query.filter(Good.goodID == orderinfo['good_id']).first()
            orderinfo = dict(orderinfo,**{'goodName':good.goodName})
            user = User.query.filter(User.userID == orderinfo['sellerID']).first()
            orderinfo = dict(orderinfo,**{'userName':user.userName})
            orderlist.append(orderinfo)

        logging.log(logging.INFO, "Get Orderlist Success: {}".format(current_user.userName))

        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data' : {'orders':orderlist}
            }
        )
    except:
        logging.log(logging.INFO, "Get Orderlist Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data':{'orders':{}}
            }
        )


@login_required
@api.route('/list_buyer_orders', methods = ['POST'])
def list_buyer_orders():
    '''
    列出作为买家的订单
    :param:     [JSON]
        "start"
        "count"
        "status"
    :return:    [JSON]
        "status":  0, 1, 2, 3
        "message":
        "data": {}
    '''
    object = request.json
    buyerID = current_user.userID
    begin = object['begin']
    limit = object['limit']
    status = object['status']
    if not buyerID:
        logging.log(logging.INFO, "Get Orderlist Fail(Not Login): {}".format(current_user.userName))
        return jsonify(
            {
                'status' : 0,
                'message' : 'Fail: User Not Login',
                'data':{'orders':{}}
            }
        )

    try:
        if status == 4:
            ordersID = Order.query.filter(buyerID == Order.buyerID).offset(begin).limit(limit).all()
        else:
            ordersID = Order.query.filter(buyerID == Order.buyerID, status == Order.status).offset(begin).limit(limit).all()
        if not ordersID:
            logging.log(logging.INFO, "Get Orderlist Fail(No Order): {}".format(current_user.userName))
            return jsonify(
                {
                    'status' : 2,
                    'message' : 'Fail: No Order',
                    'data':{'orders':{}}
                }
            )
    except:
        logging.log(logging.INFO, "Get Orderlist Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data':{'orders':{}}
            }
        )

    try:
        orderlist = list()
        for row in ordersID:
            orderID = row.orderID
            orderdetail = Order.query.filter(orderID == Order.orderID).first()
            orderinfo = {
                'orderID': orderdetail.orderID,
                'good_id': orderdetail.goodID,
                'sellerID': orderdetail.sellerID,
                'buyerID': orderdetail.buyerID,
                'createDate': orderdetail.createDate,
                'confirmDate': orderdetail.confirmDate,
                'count': orderdetail.count,
                'status': orderdetail.status
            }
            good = Good.query.filter(Good.goodID == orderinfo['good_id']).first()
            orderinfo = dict(orderinfo,**{'goodName':good.goodName})
            user = User.query.filter(User.userID == orderinfo['buyerID']).first()
            orderinfo = dict(orderinfo,**{'userName':user.userName})
            orderlist.append(orderinfo)

        logging.log(logging.INFO, "Get Orderlist Success: {}".format(current_user.userName))
        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data' : {'orders':orderlist}
            }
        )
    except:
        logging.log(logging.INFO, "Get Orderlist Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data':{'orders':{}}
            }
        )

@login_required
@api.route('/get_order_detail', methods = ['POST'])
def get_order_detail():
    '''
    获取订单详情
    :param:     [JSON]
        "orderID"
    :return:    [JSON]
        "status":  0, 1, 3
        "message":
        "data": {}
    '''

    object = request.json
    orderID = object['orderID']
    try:
        orderDetail = Order.query.filter(Order.orderID == orderID).first()

        if not orderDetail:
            logging.log(logging.INFO, "Get Order Detail Fail(No Order): {}".format(current_user.userName))
            return jsonify(
                {
                    'status':0,
                    'message':'No Such Order',
                    'Data':{}
                }
            )

        logging.log(logging.INFO, "Get Order Detail Sucess(): {}".format(current_user.userName))
        return jsonify(
            {
                'status' : 1,
                'message' : 'Success',
                'data' : {
                    'orderID': orderDetail.orderID,
                    'good_id': orderDetail.goodID,
                    'sellerID': orderDetail.sellerID,
                    'buyerID': orderDetail.buyerID,
                    'createDate': orderDetail.createDate,
                    'confirmDate': orderDetail.confirmDate,
                    'count': orderDetail.count,
                    'status': orderDetail.status
                }
            }
        )

    except:
        logging.log(logging.INFO, "Get Order Detail Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 3,
                'message': 'Fail: Database Error',
                'data': {}
            }
        )


@login_required
@api.route('/create_order',methods = ['POST'])
def create_order():
    '''
    创建新订单
    :param:     [JSON]
        "good_id"
        "sellerID"
        "count"
    :return:    [JSON]
        "status":  1, 2, 3
        "message":
        "data": {}
    '''

    neworderinfo = request.json
    timenow = datetime.utcnow()
    neworderinfo['buyerID'] = current_user.userID

    if neworderinfo['sellerID'] == neworderinfo['buyerID']:
        logging.log(logging.INFO, "Create Order Fail(Same User): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 2,
                'message': 'Same Seller and Buyer',
                'data': {}
            }
        )

    try:
        neworder = Order(
            goodID = neworderinfo['good_id'],
            sellerID = neworderinfo['sellerID'],
            buyerID = neworderinfo['buyerID'],
            createDate = timenow,
            confirmDate = timenow,
            count = neworderinfo['count'],
            status = 0
        )
        db.session.add(neworder)
        db.session.commit()

        logging.log(logging.INFO, "Create Order Success(): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 1,
                'message': 'Success',
                'data':{'orderID':neworder.orderID}
            }
        )

    except:
        logging.log(logging.INFO, "Create Order Fail(Database): {}".format(current_user.userName))
        return jsonify(
            {
                'status': 3,
                'message': 'Database Error',
                'data':{}
            }
        )


@login_required
@api.route('/confirm_order',methods = ['POST'])
def confirm_order():
    '''
    确认订单
    :param:     [JSON]
        "orderID"
    :return:    [JSON]
        "status":  1, 2, 3 ,4 ,5
        "message":
        "data": {}

    P.S. 状态 0：未确认  1：买家单方面确认  2：卖家单方面确认 3：已确认
    '''

    object = request.json
    userID = current_user.userID
    orderID = object['orderID']

    try:
        order = Order.query.filter(Order.orderID == orderID).first()
        if not order:
            logging.log(logging.INFO, "Confirm Order Fail(No Order): {}".format(current_user.userName))
            return jsonify(
                {
                    'status':2,
                    'message': 'No Such Order',
                    'data':{}
                }
            )

    except:
        logging.log(logging.INFO, "Confirm Order Fail(Database): {}".format(current_user.userName))
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
                logging.log(logging.INFO, "Confirm Order Fail(No Auth): {}".format(current_user.userName))
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status':currentStatus }
                    }
                )

            logging.log(logging.INFO, "Confirm Order Success(): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{'status': currentStatus }
                }
            )

        except:
            logging.log(logging.INFO, "Confirm Order Fail(Database): {}".format(current_user.userName))
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
                logging.log(logging.INFO, "Confirm Order Fail(Already Confirmed): {}".format(current_user.userName))
                return jsonify(
                    {
                        'status': 5,
                        'message': 'You Hava Already Confirmed',
                        'data': {'status': currentStatus }
                    }
                )
            else:
                logging.log(logging.INFO, "Confirm Order Fail(No Auth): {}".format(current_user.userName))
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status': currentStatus }
                    }
                )

            logging.log(logging.INFO, "Confirm Order Success(): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data':{'status': currentStatus }
                }
            )

        except:
            logging.log(logging.INFO, "Confirm Order Fail(Database): {}".format(current_user.userName))
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
                logging.log(logging.INFO, "Confirm Order Fail(Already Confirmed): {}".format(current_user.userName))
                return jsonify(
                    {
                        'status': 5,
                        'message': 'You Hava Already Confirmed',
                        'data': {'status': currentStatus }
                    }
                )
            else:
                logging.log(logging.INFO, "Confirm Order Fail(No Auth): {}".format(current_user.userName))
                return jsonify(
                    {
                        'status': 4,
                        'message': 'User Is Not Either Buyer Or Seller',
                        'data': {'status': currentStatus }
                    }
                )

            logging.log(logging.INFO, "Confirm Order Success(): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 1,
                    'message': 'Success',
                    'data': {'status': currentStatus }
                }
            )

        except:
            logging.log(logging.INFO, "Confirm Order Fail(Database): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 3,
                    'message': 'Datebase Error',
                    'data': {'status': currentStatus }
                }
            )
    else:
        if userID == order.buyerID or userID == order.sellerID:
            logging.log(logging.INFO, "Confirm Order Fail(Already Confirmed): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 5,
                    'message': 'You Hava Already Confirmed',
                    'data': {'status': currentStatus }
                }
            )
        else:
            logging.log(logging.INFO, "Confirm Order Fail(No Auth): {}".format(current_user.userName))
            return jsonify(
                {
                    'status': 4,
                    'message': 'User Is Not Either Buyer Or Seller',
                    'data': {'status': currentStatus }
                }
            )




