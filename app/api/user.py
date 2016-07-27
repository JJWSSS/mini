# -*- coding: utf-8 -*-
from . import api
from flask import request, jsonify, current_app
from ..models import User
from .. import db
from flask_login import login_user, logout_user, login_required, current_user
from ..models import generate_password_hash, check_password_hash
import logging
from werkzeug.utils import secure_filename
import os
from PIL import Image
from random import randint


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


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
    try:
        password = objects["password"]
        username = str(objects['username'])
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
    # Query if it exist
    beseen = db.session.query(User).filter_by(userName=username).first()
    # If The phone number had been Used, return failure
    if beseen:
        return jsonify({
            "status" : 0,
            "message" : "Register Fail, The username has been Used!",
            "data"   : {}
        })
    head_photo = "img/default/" + str(randint(1,5)) + ".png"
    try:
        newuser = User(userName=username, password_hash=generate_password_hash(password), nickName=username, picture=head_photo, compressPicture=head_photo)
        db.session.add(newuser)
        db.session.commit()
    except Exception as e:
        # Database Or Internal Error
        logging.log(logging.ERROR, "Database Error Occure, details: {}".format(e.message))
        return jsonify({
            "status": 2,
            "message": "Unknown Error Occur in the Database Manage",
            "data": {}
        })
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
    try:
        username = objects["username"]
        password = objects["password"]
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
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
            "data": {
                "username": username,
                "id": person.userID,
                "nickname": person.nickName,
                "email": person.email,
                "isAuthenticated": person.isAuthenticated,
                "qq": person.qq,
                "picture": person.picture,
                "compressPicture": person.compressPicture
            }
        })
    else :
        logging.log(logging.DEBUG, "Login Fail(Password): {}".format(username))
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
def reset_password():
    '''
        logout
        :param:    [JSON]
            "username",
            "oldpasswd",
            "newpasswd"
        :return:    [JSON]
            "status" : 0,
            "message" : "reset Successful",
            "data"   : {}
        '''
    objects = request.json
    try:
        username = objects['username']
        oldpasswd = objects['oldpasswd']
        newpasswd = objects['newpasswd']
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
    person = User.query.filter_by(userName=username).first()
    if person:
        # Check For Password
        if check_password_hash(person.password_hash, oldpasswd) :
            hash_passwd = generate_password_hash(newpasswd)
            # Exception Solution
            for i in range(0, 3):
                try:
                    person.password_hash = hash_passwd
                    db.session.commit()
                    break
                except:
                    # logging
                    db.session.rollback()
                    db.session.remove()
                    if i is 2 :
                        return jsonify({
                            "status": 2,
                            "message": "Something Error Occur With Database",
                            "data": {}
                        })
        else:
            # Error : Old PassWord is Wrong
            return jsonify({
                "status": 0,
                "message": "Password Is Error",
                "data": {}
            })
    else:
        # Error: No such User
        return jsonify({
            "status": 0,
            "message": "Not such User",
            "data": {}
        })
    # Success
    return jsonify({
        "status": 1,
        "message": "Reset Successful",
        "data": {}
    })


@api.route('/forget', methods=['POST'])
@login_required
def forget_passwd():
    '''
        logout
        :param:    [JSON]
            "username",
            "newpasswd"
        :return:    [JSON]
            "status" : 0,
            "message" : "reset Successful",
            "data"   : {}
        '''
    objects = request.json
    try:
        username  = objects["username"]
        newpasswd = objects["password"]
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
    person = User.query.filter_by(userName=username).first()
    if person :
        for i in range(0, 3):
            try:
                person.password_hash = generate_password_hash(newpasswd)
                db.session.commit()
                break
            except Exception as e:
                logging.log(logging.WARNING, "Error Occur With Database, [ {} ]".format(e.message))
                db.session.rollback()
                db.session.remove()
                if i is 2 :
                    return jsonify({
                        "status": 2,
                        "message": "Something Error Occur With Database",
                        "data": {}
                    })
    # No such USer
    else:
        return jsonify({
            "status": 0,
            "message": "reset Password Fail! Username is Wrong",
            "data": {}
        })
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
    try:
        email = objects['email']
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
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
    user.isAuthenticated = True
    for i in range(0,3):
        try:
            db.session.commit()
        except:
            db.session.rollback()
            db.session.remove()
            logging.log(logging.ERROR, "comfirm ({}) Fail: Database or Internal Error".format(username))
            if i is 2:
                return jsonify({
                    "status": 2,
                    "message": "Something Error Occur With Database",
                    "data": {}
                })

    logging.log(logging.INFO, "comfirm({}): Success".format(username))
    return jsonify({
        "status" : 1,
        "message" : "Confirm Success",
        "data": {}
    })

def user_info(userid):
    result = User.query.filter_by(userID=userid).first()
    if result:
        logging.log(logging.INFO, "Get User Information ({}): Success".format(userid))
        return {
            "status": 1,
            "message": "Get user info Success",
            "data": {
                "username": result.userName,
                "id": result.userID,
                "nickname": result.nickName,
                "email": result.email,
                "isAuthenticated": result.isAuthenticated,
                "qq": result.qq,
                "picture":result.picture,
                "compressPicture":result.compressPicture
            }
        }
    else:
        logging.log(logging.INFO, "Get User Information ({}) Fail: No such User".format(userid))
        return {
            "status": 0,
            "message": "Get User info Fail!, Not such User",
            "data": {}
        }

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
                "qq": result.qq,
                "picture":result.picture,
                "compressPicture":result.compressPicture
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
    try:
        nickname = objects["nickname"]
        picture = objects["picture_url"]
        compressPicture = objects["compressPicture_url"]
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['JSON Param Not Match', k.args]})
    result = User.query.filter_by(userName=username).first()
    if result:
        if result.isAuthenticated is False :
            logging.log(logging.INFO, "Update User Information ({}) Fail: No Authentiaction".format(username))
            return jsonify({
                "status": 2,
                "message": "Update User Fail!, The user has no Auth",
                "data" : {}
            })
        for i in range(0, 3):
            try:
                result.nickName = nickname
                result.picture = picture
                result.compressPicture = compressPicture
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                db.session.remove()
                logging.log(logging.ERROR, "Update User Information ({}) Fail: Database or Internal Error".format(username))
                if i is 2:
                    return jsonify({
                        "status": 2,
                        "message": "Something Error Occur With Database",
                        "data": {}
                    })
    # No Such User
    else :
        logging.log(logging.INFO, "Update User Information ({}) Fail: No such User".format(username))
        return jsonify({
            "status": 0,
            "message": "Update User Fail!, Not such User",
            "data" : {}
        })

    logging.log(logging.DEBUG, "Update User Information ({}): Success".format(username))
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
                "isAuth"   : current_user.isAuthenticated,
                "username" : current_user.username,
                "email"    : current_user.email,
                "qq"       : current_user.qq,
                "compressPicture": current_user.compressPicture
            }
        })

@api.route('/user_picture',methods=['POST'])
def user_photo():
    try:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            url = os.path.join(current_app.config['UPLOAD_FOLDER'], (str(randint(1, 100))+filename))
            file.save(url)
            im = Image.open(url)
            im.thumbnail((200, 200))
            compress_url = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                        ('compress_'+str(randint(1, 100))+filename))
            im.save(compress_url)
            return jsonify({
                'status': 1,
                'data': {
                    'picture': url,
                    'compressPicture': compress_url
                }
            })
        elif not file:
            return jsonify({
                'status': -2,
                'data': '文件为空'
            })
        else:
            return jsonify({
                'status': -3,
                'data': '文件名后缀不符合要求'
                })
    except KeyError as k:
        return jsonify({
            'status': 0,
            'data': ['json参数不对', k.args]
        })
    except FileNotFoundError as f:
        return jsonify({
            'status': -1,
            'data': ['文件夹没有创建或路径不对', f.args]
        })
    except Exception as e:
        return jsonify({
            'status': -2,
            'data': ['未知错误', e.args]
        })


