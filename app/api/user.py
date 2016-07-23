# -*- coding: utf-8 -*-
from . import api
from flask import request, jsonify, g
from ..models import User
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from ..models import generate_password_hash

# register: first step
# make a new user with incomlete Message
# param[POST]:
#             "telephone"
#             "password"
@api.route('/register', methods=['POST'])
def register():
    objects = request.json
    password = objects["password"]
    username = str(objects['telephone'])
    # Query if it exist
    beseen = db.session.query(User).filter_by(userName=username).first()
    # If The phone number had been Used, return failure
    if beseen:
        return jsonify({
            "status" : 1,
            "message" : "Register Fail, The username has been Used!",
            "data"   : {}
        })
    try:
        newuser = User(userName=username, password_hash=generate_password_hash(password), nickName=username)
        db.session.add(newuser)
    except Exception as e:
        return jsonify({
            "status": 2,
            "message": "Unknown Error Occur in the Database Manage",
            "data": {}
        })
    db.session.commit()
    return jsonify({
        "status" : 0,
        "message" : "Register Success",
        "data": {}
    }), 200

# login
# param[POST]:
#             "username"
#             "password"
# return[HTML][JSON]
#             "status":  0, 1
#             "message":
@api.route('/login', methods=['POST'])
def login():
    objects = request.json
    username = objects["username"]
    password = objects["password"]
    # Fetch User's information From database
    person = User.query.filter_by(userName=username).first()
    if person :
        pass
        #print 'username={}, password={}'.format(person.userName, person.password_hash)
    else:
        return jsonify({
            "status" : 1,
            "message" : "Login Failure, Username is not Exist",
            "data": {}
        })
    if person.verify_password(password=password) :
        login_user(person, True)
        return jsonify({
            "status": 0,
            "message": "Login Success",
            "data": {}
        }), 200
    else :
        return jsonify({
            "status": 2,
            "message": "Login Failure, Password is Wrong",
            "data": {}
        })

# logout
@login_required
@api.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({
        "status" : 0,
        "message" : "logout Success",
        "data": {}
    }), 200

# reset user's password
# TODO
@api.route('/reset', methods=['POST'])
def reset_passwd():
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
            return jsonify({
                "status": 2,
                "message": "Something Error Occur With Database",
                "data": {}
            })
    else:
        return jsonify({
            "status": 1,
            "message": "reset Password Fail! Username is Wrong",
            "data": {}
        })
    return jsonify({
        "status": 0,
        "message": "reset Success",
        "data": {}
    })

# register: second step
# comfirm the User's Message by tencent email
# param[POST]
#             "email"
# return[HTML][JSON]
#                   "status": 0, 1
#                   "message":
@login_required
@api.route('/comfirm', methods=['POST'])
def comfirm():
    objects = request.json
    username  = current_user.userName
    email = objects['email']
    # Fetch User's Information From database
    user = User.query.filter_by(userName=username).first()
    if user :
        user.email = email
    else:
        return jsonify({
            "status" : 1,
            "message" : "Confirm Failure, Not such user",
            "data": {}
        })
    db.session.commit()
    # TODO Send Active E-amil
    user.isAuthenticated = True
    db.session.commit()
    return jsonify({
            "status" : 0,
            "message" : "Confirm Success",
            "data": {}
    }), 200

# get user's information
# return[HTML][JSON]  When "status" is 0, then has the other Attributes
#                   "status"  : 0, 1
#                   "message" :
#                   "username":
#                   "id"      :
#                   "nickname":
#                   "email"   :
#                   "isAuthenticated":
#                   "qq"      :
@login_required
@api.route('/getuser', methods=['GET'])
def get_user_info():
    username = current_user.userName
    result = User.query.filter_by(userName=username).first()
    if result:
        return jsonify({
            "status"   : 0,
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
        return jsonify({
            "status"    : 1,
            "message"   : "Get User info Fail!, Not such User",
            "data": {}
        })


# update user's information
# param[POST][JSON]
#            "nickname"
# return[HTML][JSON]
#            "status" : 0, 1, 2  (Success, Fail with No user, Fail with no Auth)
#            "message" :
@login_required
@api.route('/updateuser', methods=['POST'])
def update_user_info():
    objects = request.json
    username = current_user.userName
    nickname = objects["nickname"]
    result = User.query.filter_by(userName=username).first()
    if result:
        if result.isAuthenticated is False :
            return jsonify({
                "status": 2,
                "message": "Update User Fail!, The user has no Auth",
                "data" : {}
            })
        result.nickName = nickname
        db.session.commit()
    else :
        return jsonify({
            "status": 1,
            "message": "Update User Fail!, Not such User",
            "data" : {}
        })
    return jsonify({
        "status" : 0,
        "message" : "Update User Success!",
        "data" : {}
    })


@api.route('/active', methods=['GET, POST'])
def is_it_active():
    if current_user.is_anonymous():
        return jsonify({
            "status": 1,
            "message": "User Not Login!",
            "data": {}
        })
    else :
        return jsonify({
            "status": 0,
            "message": "User has Login!",
            "data": {}
        })


