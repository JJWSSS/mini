# -*- coding: utf-8 -*-
from . import api
from flask import request, jsonify, g
from ..models import User
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from ..models import generate_password_hash
import logging

@api.route('/register', methods=['POST'])
def register():
    '''
    register: first step
    make a new user with incomlete Message
    :param:   [JSON]
      "telephone"
      "password"
    :return:  [JSON]
       "status" : 0,
       "message" : "",
       "data"   : {}
    '''
    objects = request.json
    password = objects["password"]
    username = str(objects['username'])
    # Query if it exist
    beseen = db.session.query(User).filter_by(userName=username).first()
    # If The phone number had been Used, return failure
    if beseen:
        return jsonify({
            "status" : 0,
            "message" : "Register Fail, The username has been Used!",
            "data"   : {}
        })
    try:
        newuser = User(userName=username, password_hash=generate_password_hash(password), nickName=username)
        db.session.add(newuser)
    except Exception as e:
        # Database Or Internal Error
        logging.log(logging.ERROR, "Database Error Occure, details: {}".format(e.message))
        return jsonify({
            "status": 2,
            "message": "Unknown Error Occur in the Database Manage",
            "data": {}
        })
    db.session.commit()
    logging.log(logging.INFO, "Register Success: username{}".format(username))
    return jsonify({
        "status" : 1,
        "message" : "Register Success",
        "data": {}
    })

@api.route('/login', methods=['POST'])
def login():
    '''
    login
    :param:   [JSON]
        "username"
        "password"
    :return:  [JSON]
        "status":  0, 1
        "message":
        "data": {}
    '''
    objects = request.json
    username = objects["username"]
    password = objects["password"]
    # Fetch User's information From database
    person = User.query.filter_by(userName=username).first()
    if person :
        pass
        #print 'username={}, password={}'.format(person.userName, person.password_hash)
    else:
        logging.log(logging.INFO, "Login Fail: {}".format(username))
        return jsonify({
            "status" : 0,
            "message" : "Login Failure, Username is not Exist",
            "data": {}
        })
    if person.verify_password(password=password) :
        login_user(person, True)
        logging.log(logging.INFO, "Login Success: {}".format(username))
        return jsonify({
            "status": 1,
            "message": "Login Success",
            "data": {}
        })
    else :
        logging.log(logging.INFO, "Login Fail(Password): {}".format(username))
        return jsonify({
            "status": 2,
            "message": "Login Failure, Password is Wrong",
            "data": {}
        })

@login_required
@api.route('/logout', methods=['POST'])
def logout():
    '''
    logout
    :param:

    :return:    [JSON]
        "status" : 0,
        "message" : "Register Fail, The username has been Used!",
        "data"   : {}
    '''
    logout_user()
    return jsonify({
        "status" : 1,
        "message" : "logout Success",
        "data": {}
    })

# reset user's password
# TODO
@api.route('/reset', methods=['POST'])
def reset_passwd():
    '''
    reset password without login
    :param:    [JSON]

    :return:   [JSON]
        "status" : 0,
        "message" : "",
        "data": {}
    '''
    objects = request.json
    username  = objects["username"]
    newpasswd = objects["password"]
    person = User.query.filter_by(userName=username).first()
    if person :
        try:
            person.password_hash = generate_password_hash(newpasswd)
            db.session.commit()
        except Exception as e:
            # logging
            logging.log(logging.ERROR, "reset password({}) Fail: Database or Internal ERROR".format(username))
            return jsonify({
                "status": 2,
                "message": "Something Error Occur With Database",
                "data": {}
            })
    else:
        logging.log(logging.INFO, "reset password({}) Fail: Not Such username".format(username))
        return jsonify({
            "status": 0,
            "message": "reset Password Fail! Username is Wrong",
            "data": {}
        })
    logging.log(logging.INFO, "reset password({}): Success".format(username))
    return jsonify({
        "status": 1,
        "message": "reset Success",
        "data": {}
    })

@login_required
@api.route('/comfirm', methods=['POST'])
def comfirm():
    '''
    register: second step
    comfirm the User's Message by tencent email
    :param:  [JSON]
        "email"
    :return: [JSON]
        "status" : 0,
        "message" : "",
        "data": {}
    '''
    objects = request.json
    username  = current_user.userName
    email = objects['email']
    # Fetch User's Information From database
    user = User.query.filter_by(userName=username).first()
    if user :
        user.email = email
    else:
        logging.log(logging.INFO, "comfirm ({}) Fail: No Such User".format(username))
        return jsonify({
            "status" : 0,
            "message" : "Confirm Failure, Not such user",
            "data": {}
        })
    #db.session.commit()
    # TODO Send Active E-amil
    try:
        user.isAuthenticated = True
        db.session.commit()
    except:
        logging.log(logging.ERROR, "comfirm ({}) Fail: Database or Internal Error".format(username))
    logging.log(logging.INFO, "comfirm({}): Success".format(username))
    return jsonify({
            "status" : 1,
            "message" : "Confirm Success",
            "data": {}
    })

@login_required
    @api.route('/getuser', methods=['GET'])
def get_user_info():
    '''
    get current user's information
    :param:

    :return:   [JSON]
        "status"   : 1,
        "message"  : "",
        "data": {
            "username": username,
            "id": result.userID,
            "nickname": result.nickName,
            "email": result.email,
            "isAuthenticated": result.isAuthenticated,
            "qq": result.qq
        }
    '''
    username = current_user.userName
    result = User.query.filter_by(userName=username).first()
    if result:
        logging.log(logging.INFO, "Get User Information ({}): Success".format(username))
        return jsonify({
            "status"   : 1,
            "message"  : "Get user info Success",
            "data": {
                "username": username,
                "id": result.userID,
                "nickname": result.nickName,
                "email": result.email,
                "isAuthenticated": result.isAuthenticated,
                "qq": result.qq
            }
        })
    else :
        logging.log(logging.INFO, "Get User Information ({}) Fail: No such User".format(username))
        return jsonify({
            "status"    : 0,
            "message"   : "Get User info Fail!, Not such User",
            "data": {}
        })


@login_required
@api.route('/updateuser', methods=['POST'])
def update_user_info():
    '''
    update User's Information
    :param:   [JSON]
        "nickname"
    :return:  [JSON]
        "status": 2,
        "message": "",
        "data" : {}
    '''
    objects = request.json
    username = current_user.userName
    nickname = objects["nickname"]
    result = User.query.filter_by(userName=username).first()
    if result:
        if result.isAuthenticated is False :
            logging.log(logging.INFO, "Update User Information ({}) Fail: No Authentiaction".format(username))
            return jsonify({
                "status": 2,
                "message": "Update User Fail!, The user has no Auth",
                "data" : {}
            })
        try:
            result.nickName = nickname
            db.session.commit()
        except Exception as e:
            logging.log(logging.ERROR, "Update User Information ({}) Fail: Database or Internal Error".format(username))
    else :
        logging.log(logging.INFO, "Update User Information ({}) Fail: No such User".format(username))
        return jsonify({
            "status": 0,
            "message": "Update User Fail!, Not such User",
            "data" : {}
        })
    logging.log(logging.INFO, "Update User Information ({}): Success".format(username))
    return jsonify({
        "status" : 1,
        "message" : "Update User Success!",
        "data" : {}
    })


@api.route('/active', methods=['GET'])
def is_it_active():
    '''
    If Ip is Active
    :param:

    :return:   [JSON]
        "status": 0,
        "message": "User Not Login!",
        "data": {}
    '''
    if current_user.is_anonymous():
        return jsonify({
            "status": 0,
            "message": "User Not Login!",
            "data": {}
        })
    else :
        return jsonify({
            "status": 1,
            "message": "User has Login!",
            "data": {
                "id"       : current_user.userID,
                "nickname" : current_user.nickName,
                "isAuth"   : current_user.isAuthenticated
            }
        })


