# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify, g, current_app
from ..models import User, Good
from .. import db
from werkzeug.utils import secure_filename
import os
from PIL import Image
from datetime import datetime
from random import randint
from flask_login import login_required, current_user


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@api.route('/goods/', methods=['POST'])
def get_goods():
    """
    功能: 获取商品列表
    参数类型: json
    参数: userID(卖家的ID), type(商品类型), begin(查询起始位置), limit(查询个数)
    返回类型: json
    参数: status(1为成功, 0为失败), data(商品列表数据)
    """
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        if userid:
            if type:
                if begin or limit:
                    goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).all()
            elif begin or limit:
                goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).all()
        elif type:
            if begin or limit:
                goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).all()
        else:
            goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
        return jsonify({'status': 1, 'data': {'goods': [good.to_json() for good in goods]}})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except AttributeError:
        return jsonify({'status': -1, 'data': ['未查到数据', AttributeError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/good/', methods=['POST'])
def single_good():
    try:
        good = Good.query.get(request.json['good_id'])
        return jsonify({'status': 1, 'data': good.to_json()})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except AttributeError:
        return jsonify({'status': -1, 'data': ['未查到数据', AttributeError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/search/', methods=['POST'])
def search():
    try:
        search_name = request.json['search_name']
        goods = Good.query.filter(Good.goodName.ilike('%'+search_name+'%')).all()
        return jsonify({'status': 1, 'data': {'result': [good.to_json() for good in goods]}})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except AttributeError:
        return jsonify({'status': -1, 'data': ['未查到数据', AttributeError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/new_good/', methods=['POST'])
@login_required
def new_good():
    try:
        objects = request.json
        good = Good(goodName=objects['goodName'], description=objects['description'],
                    freeCount=objects['freeCount'], type=objects['type'],
                    contact_tel=objects['contact_tel'], price=objects['price'], contact_qq=objects['contact_qq'],
                    contact_wechat=objects['contact_wechat'], image=objects['image_url'],
                    compressImage=objects['compress_url'], poster=objects['poster'], address=objects['address'])
        good.seller = current_user
        db.session.add(good)
        db.session.commit()
        return jsonify({'status': 1, 'data': good.to_json()})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/new_photo/', methods=['POST'])
@login_required
def new_photo():
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
            return jsonify({'status': 1, 'data': {'image': url, 'compress_image': compress_url}})
        elif not file:
            return jsonify({'status': -2, 'data': '文件为空'})
        else:
            return jsonify({'status': -3, 'data': '文件名后缀不符合要求'})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except FileNotFoundError:
        return jsonify({'status': -1, 'data': ['文件夹没有创建或路径不对', FileNotFoundError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/edit_good/', methods=['POST'])
def edit_good():
    try:
        objects = request.json
        good = Good.query.get(objects['good_id'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        good.description = objects['description']
        good.goodName = objects['goodName']
        good.modifyDate = datetime.utcnow()
        good.contact_tel = objects['contact_tel']
        good.contact_qq = objects['contact_qq']
        good.contact_wechat = objects['contact_wechat']
        good.price = objects['price']
        good.address = objects['address']
        good.poster = objects['poster']
        db.session.add(good)
        db.session.commit()
        return jsonify({'status': 1, 'data': good.to_json()})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/delete_good/', methods=['POST'])
@login_required
def delete_good():
    try:
        good = Good.query.get(request.json['good_id'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        db.session.delete(good)
        return jsonify({'status': 1, 'data': {}})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/homepage_goods/', methods=['POST'])
def homepage_goods():
    try:
        objects = request.json
        goods_dict = dict()
        for i in range(8):
            goods = Good.query.filter_by(type=i).order_by(Good.createDate.desc()).limit(objects['limit']).all()
            goods_dict[str(i)] = [good.to_json() for good in goods]
        return jsonify({'status': 1, 'data': goods_dict})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/refresh_goods/', methods=['POST'])
def refresh_goods():
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
        if userid:
            if type:
                if begin or limit:
                    goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).all()
            elif begin or limit:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).all()
        elif type:
            if begin or limit:
                goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).all()
        else:
            goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
        if goods:
            return jsonify({'status': 1, 'data': [good.to_json() for good in goods]})
    except ValueError:
        return jsonify({'status': -1, 'data': ['日期格式有误', ValueError.args]})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/more_goods/', methods=['POST'])
def more_goods():
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
        if userid:
            if type:
                if begin or limit:
                    goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).all()
            elif begin or limit:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).all()
        elif type:
            if begin or limit:
                goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).all()
        else:
            goods = Good.query.offset(begin).limit(limit).order_by(Good.createDate.desc()).all()
        if goods:
            return jsonify({'status': 1, 'data': [good.to_json() for good in goods]})
    except ValueError:
        return jsonify({'status': -1, 'data': ['日期格式有误', ValueError.args]})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/add_times/', methods=['POST'])
def add_times():
    try:
        good = Good.query.get(request.json['goodID'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        good.times += 1
        db.session.add(good)
        return jsonify({'status': 1, 'data': {}})
    except KeyError:
        return jsonify({'status': 0, 'data': ['json参数不对', KeyError.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


