# -*- coding: utf-8 -*-

from . import api
from flask import request, jsonify, g, current_app
from ..models import User, Good, Comment
from .. import db
from werkzeug.utils import secure_filename
import os
from PIL import Image
from datetime import datetime
from random import randint
from flask_login import login_required, current_user
from sqlalchemy.orm.exc import UnmappedInstanceError


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in current_app.config['ALLOWED_EXTENSIONS']


@api.route('/goods', methods=['POST'])
def get_goods():
    """
    功能: 获取商品列表
    参数类型: json
    参数: userID(卖家的ID), type(商品类型), begin(查询起始位置), limit(查询个数)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        if userid:
            if type == -1:
                if limit:
                    goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter_by(sellerID=userid, type=type).order_by(Good.createDate.desc()).offset(begin).all()
            elif limit:
                goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(sellerID=userid).order_by(Good.createDate.desc()).offset(begin).all()
        elif type == -1:
            if limit:
                goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter_by(type=type).order_by(Good.createDate.desc()).offset(begin).all()
        else:
            if limit:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).all()
        return jsonify({'status': 1, 'data': {'goods': [good.to_json() for good in goods]}})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except AttributeError as a:
        return jsonify({'status': -1, 'data': ['未查到数据', a.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/good', methods=['POST'])
def single_good():
    """
    功能: 获取商品详情
    参数类型: json
    参数: good_id(卖家的ID)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品数据)
    """
    try:
        good = Good.query.get(request.json['good_id'])
        return jsonify({'status': 1, 'data': good.to_json()})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except AttributeError as a:
        return jsonify({'status': -1, 'data': ['未查到数据', a.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/search', methods=['POST'])
def search():
    """
    功能: 搜索商品(根据商品名称)
    参数类型: json
    参数: search_name(搜索名称)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        search_name = request.json['search_name']
        goods = Good.query.filter(Good.goodName.ilike('%'+search_name+'%')).all()
        return jsonify({'status': 1, 'data': {'result': [good.to_json() for good in goods]}})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except AttributeError as a:
        return jsonify({'status': -1, 'data': ['未查到数据', a.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/new_good', methods=['POST'])
def new_good():
    """
    功能: 添加新商品
    参数类型: json
    参数: 一系列商品信息
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        objects = request.json
        if float(objects['price']) < 0:
            return jsonify({'status': -3, 'data': ['价格为负']})
        if int(objects['freeCount']) < 0:
            return jsonify({'status': -4, 'data': ['剩余数量为负']})
        good = Good(goodName=objects['goodName'], description=objects['description'],
                    freeCount=objects['freeCount'], type=objects['type'],
                    contact_tel=objects['contact_tel'], price=objects['price'], contact_qq=objects['contact_qq'],
                    contact_wechat=objects['contact_wechat'], image=objects['image_url'],
                    compressImage=objects['compress_url'], poster=objects['poster'], address=objects['address'])
        good.seller = current_user
        db.session.add(good)
        db.session.commit()
        return jsonify({'status': 1, 'data': good.to_json()})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/new_photo', methods=['POST'])
def new_photo():
    """
    功能: 添加新的商品图片
    参数类型: json
    参数: 图片(二进制信息)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为文件夹没创建或路径不对, -2为未知错误, -3为文件为空, -4为文件名后缀不符合),
        data(商品列表数据)
    """
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
            return jsonify({'status': -3, 'data': '文件为空'})
        else:
            return jsonify({'status': -4, 'data': '文件名后缀不符合要求'})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except FileNotFoundError as f:
        return jsonify({'status': -1, 'data': ['文件夹没有创建或路径不对', f.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/edit_good', methods=['POST'])
def edit_good():
    """
    功能: 修改商品信息
    参数类型: json
    参数: 所需修改的商品信息
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误, -3为价格为负), data(商品列表数据)
    """
    try:
        objects = request.json
        good = Good.query.get(objects['good_id'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        if float(objects['price']) < 0:
            return jsonify({'status': -3, 'data': ['价格为负']})
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
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/delete_good', methods=['POST'])
def delete_good():
    """
    功能: 删除商品
    参数类型: json
    参数: good_id(商品的ID)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        good = Good.query.get(request.json['good_id'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        comments = Comment.query.filter_by(goodsID=request.json['good_id']).all()
        db.session.delete(comments)
        db.session.delete(good)
        return jsonify({'status': 1, 'data': ["有comment"]})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/homepage_goods', methods=['POST'])
def homepage_goods():
    """
    功能: 首页商品列表
    参数类型: json
    参数: limit(每一个类别的数量)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -2为未知错误), data(商品列表数据)
    """
    try:
        objects = request.json
        goods_dict = dict()
        for i in range(10):
            goods = Good.query.filter_by(type=i).order_by(Good.createDate.desc()).limit(objects['limit']).all()
            goods_dict[str(i)] = [good.to_json() for good in goods]
        return jsonify({'status': 1, 'data': goods_dict})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/refresh_goods', methods=['POST'])
def refresh_goods():
    """
    功能: 刷新商品列表
    参数类型: json
    参数: userID(卖家的ID), type(商品类型), begin(查询起始位置), limit(查询个数), datetime(日期时间)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
        if userid:
            if type == -1:
                if limit:
                    goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).all()
            elif limit:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate > day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).all()
        elif type == -1:
            if limit:
                goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate > day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).all()
        else:
            if limit:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).all()
        return jsonify({'status': 1, 'data': [good.to_json() for good in goods]})
    except ValueError as v:
        return jsonify({'status': -1, 'data': ['日期格式有误', v.args]})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/more_goods', methods=['POST'])
def more_goods():
    """
    功能: 加载更多商品
    参数类型: json
    参数: userID(卖家的ID), type(商品类型), begin(查询起始位置), limit(查询个数), datetime(日期时间)
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        objects = request.json
        userid = objects['userID']
        type = objects['type']
        begin = objects['begin']
        limit = objects['limit']
        day_time = datetime.strptime(objects['datetime'], '%a, %d %b %Y %X GMT')
        if userid:
            if type == -1:
                if limit:
                    goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
                else:
                    goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid, Good.type == type).order_by(Good.createDate.desc()).offset(begin).all()
            elif limit:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate < day_time, Good.sellerID == userid).order_by(Good.createDate.desc()).offset(begin).all()
        elif type == -1:
            if limit:
                goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.filter(Good.createDate < day_time, Good.type == type).order_by(Good.createDate.desc()).offset(begin).all()
        else:
            if limit:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).limit(limit).all()
            else:
                goods = Good.query.order_by(Good.createDate.desc()).offset(begin).all()
        return jsonify({'status': 1, 'data': [good.to_json() for good in goods]})
    except ValueError as v:
        return jsonify({'status': -1, 'data': ['日期格式有误', v.args]})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


@api.route('/add_times', methods=['POST'])
def add_times():
    """
    功能: 增加点击次数
    参数类型: json
    参数: good_id
    返回类型: json
    参数: status(1为成功, 0为json参数不对, -1为未查到数据, -2为未知错误), data(商品列表数据)
    """
    try:
        good = Good.query.get(request.json['good_id'])
        if not good:
            return jsonify({'status': -1, 'data': ['商品没有查到']})
        if not good.times:
            good.times = 1
        else:
            good.times += 1
        db.session.add(good)
        return jsonify({'status': 1, 'data': {}})
    except KeyError as k:
        return jsonify({'status': 0, 'data': ['json参数不对', k.args]})
    except Exception as e:
        return jsonify({'status': -2, 'data': ['未知错误', e.args]})


