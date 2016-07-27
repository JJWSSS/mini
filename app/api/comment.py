# coding=utf-8
from app.api import api
from app.models import Comment
from flask import request
from flask import jsonify
import copy
from app import db
from manage import app
import logging
from functools import wraps
from app.api import user


def append_user_info(get_json):
    """
    用于在获取评论列表的返回数据中附上用户信息的装饰器，
    装饰CommentProxy.query方法用
    """
    @wraps(get_json)
    def __do_append_image(self, args):
        ret = get_json(self, args)
        for item in ret:
            user_info = user.user_info(item['commentatorID'])
            if user_info['status']:
                item['userInfo'] = {
                    'userNmae': user_info['data']['username'],
                    'nickName': user_info['data']['nickname'],
                    'id': user_info['data']['id']
                }
            else:
                item['userInfo'] = None
        return ret

    return __do_append_image


def model_to_json(get_all):
    """
    用于装饰CommentProxy.query方法用的装饰器，
    将查询结果从模型对象转换为Json格式的数据
    """
    @wraps(get_all)
    def __do_to_json(self, args):
        ret = get_all(self, args)
        proxy = __make_comment_proxy()
        return [proxy.to_json(item) for item in ret]

    return __do_to_json


def get_all(qurey):
    """
    用于装饰CommentProxy.query的装饰器，取出查询对象中的所有结果
    """
    @wraps(qurey)
    def __do_get_all(self, args):
        return qurey(self, args).all()

    return __do_get_all


def limit_and_start_addtion(qurey):
    """
    用于装饰CommentProxy.query的装饰器，可以增加对'limit'和'start'
    参数的支持
    """
    @wraps(qurey)
    def __do_limit_and_start(self, args):
        ret = qurey(self, args)
        start = 0
        limit = 50

        if 'start' in args:
            start = args['start']
        if 'limit' in args:
            limit = args['limit']

        return ret.offset(start).limit(limit)

    return __do_limit_and_start


class CommentProxy:
    """
    Comment模型的代理类，该类负责与模型进行交互。
    该类中使用到的大部分关于模型的信息都是从配置
    中动态获得，故而与模型是一种及其松散的耦合关系
    Note:
        现在该类显然太大了，职责不单纯，除了负责操作模型
        之外，还有一些'工具方法'，这些与操作模型无关的方法
        可以提炼成为一个单独的helper类。
    """
    def __init__(self, fileds):
        """
        构造函数
        :param fileds: [list]
            该参数储存了所有模型的域(数据库表的列)名称。
        """
        self._filer_dict = {}
        self._fileds = fileds
        self.__comment = Comment

    def __getattr__(self, item):
        def _feedBack(filterx):
            self._filer_dict[item] = filterx
            return self

        return _feedBack

    @property
    def Comment(self):
        return self.__comment

    @Comment.setter
    def setComment(self, _comment):
        self.__comment = _comment

    def to_json(self, model):
        """
        将模型对象转换成为字典对象
        :param model  [Comment]:
            需要被转换的模型对象
        :return  [dict]:
            转换后的字典对象，该字典的key是模型对象的属性名,
            value 是模型对象的属性值
        """
        json_dict = {}
        for filed in self._fileds:
            json_dict[filed] = model.__getattribute__(filed)
        return json_dict

    def filter_args(self, args):
        """
        参数过滤器，用于过滤前端输入的非法参数
        :param args [dict]:
            所有请求参数的字典
        :return: [dict]
            返回的合法参数字典，字典的key是合法参数的名字，
            value是合法参数的值
        """
        ret = {}
        if args is not None:
            for key, value in args.items():
                if key in self._fileds:
                    ret[key] = value
        return ret

    @staticmethod
    def make_ret_json(status=0, messages='', data={}):
        return jsonify({'status': status, 'messages': messages, 'data': data})

    @append_user_info
    @model_to_json
    @get_all
    @limit_and_start_addtion
    def query(self, args=None):
        """
        查询函数，通过输入的查询条件查询符合条件的模型
        :param args [dict]:
            前端输入需要查询的评论之参数，
            目前包括 commentatorID 评论者的userID       [int, 非必须]
                    context       评论内容             [string, 非必须]
                    goodsID       被评论商品的goodsID  [int, 非必须]
                    commitTime    评论时间             [dataTime, 非必须]
                    commentID     评论的ID             [int, 非必须]
        :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {'comments': [ ]}
         }
        """
        if not args:
            return self.Comment.query.filter_by(status=0)

        self._filer_dict = self.filter_args(args)
        self._filer_dict['status'] = 0  # 这里假设了表的结构，依赖于表的结构，需要重构
        ret = self.Comment.query.filter_by(**self._filer_dict)
        return ret

    def insert(self, args, isVailed=None):
        """
        插入评论函数，此函数用于将一条评论插入数据库中
        :param args [dict]:
            前端输入需要插入的评论之参数，
            目前包括 commentatorID  评论者的userID     [int, 必须]
                    context        评论内容           [string, 必须]
                    goodsID       被评论商品的goodsID  [int, 必须]
        :param isVailed [function]:
            用于检查参数是否合法的检查器
        :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {'comments': [ ]}
         }
        """
        message = None
        if isVailed and not isVailed(args):
            return self.make_ret_json(0, 'invailed arguments')

        args = self.filter_args(args)
        db.session.add(self.Comment(**args))
        exp = None
        try:
            db.session.commit()
        except Exception as e:
            exp = e
            db.session.rollback()
            message = str(e)
            logging.log(logging.DEBUG, 'from comments model: ' + message)
        if exp:
            return self.make_ret_json(0, 'arguments error')
        return self.make_ret_json(1, message)

    def delete(self, args):
        """
        删除评论函数，此函数用来将一条评论从数据库中删除
        :param args [args]:
            前端输入需要删除的评论之参数，
            目前包括  commentatorID  评论者的userID     [int, 必须]
                     goodsID       被评论商品的goodsID  [int, 必须]
                    commentID     评论的ID             [int, 非必须]

        :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {'comments': [ ]}
         }        """
        self._filer_dict = self.filter_args(args)
        if len(self._filer_dict) <= 0:
            return self.make_ret_json(0, '0 comments have been deleted')
        self._filer_dict['status'] = 0
        ret = self.Comment.query.filter_by(**self._filer_dict).update({'status': 1})
        return self.make_ret_json(1, str(ret) + ' comments have been deleted')


def __make_comment_proxy():
    if hasattr(__make_comment_proxy, 'proxy'):
        return __make_comment_proxy.proxy
    table_structs = app.config.get('COMMENT_TABLE_STRUCTS')
    table_structs = copy.deepcopy(table_structs)
    table_structs.pop('__tablename__')
    proxy = CommentProxy([key for key, value in table_structs.items()])
    setattr(__make_comment_proxy, 'proxy', proxy)
    return proxy


@api.route(app.config.get('COMMENT_GET_URL'),
           methods=app.config.get('COMMENT_GET_METHODS'))
def get_comment():
    """
    获取评论接口，通过配置获取到的COMMENT_GET_URL将会被路由到该函数，
    其接受的URL参数由COMMENT_TABLE_STRUCTS配置获取
    :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {'comments': [ ]}
         }
    """
    proxy = __make_comment_proxy()
    # args = request.args
    args = request.form
    ret = proxy.query(args)
    return proxy.make_ret_json(1, data={'comments': ret})


@api.route(app.config.get('COMMENT_ADD_URL'),
           methods=app.config.get('COMMENT_ADD_METHODS'))
def add_comment():
    """
    添加评论接口，通过配置获取到的COMMENT_ADD_URL将会被路由到该函数，
    其接受的URL参数由COMMENT_TABLE_STRUCTS配置获取
    :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {（None）}
         }
    """
    proxy = __make_comment_proxy()
    args = request.form
    # args = request.args
    return proxy.insert(args)


@api.route(app.config.get('COMMENT_DELETE_URL'),
           methods=app.config.get('COMMENT_DELETE_METHODS'))
def delete_comment():
    """
    添加评论接口，通过配置获取到的COMMENT_DELETE_URL将会被路由到该函数，
    其接受的URL参数由COMMENT_TABLE_STRUCTS配置获取
    :return  [Json]:
         {
            'status' : 成功则为1，失败为0，
            'message' : 返回结果说明，
            'data' : {（None）}
         }
    """
    proxy = __make_comment_proxy()
    args = request.form
    # args = request.args
    return proxy.delete(args)
