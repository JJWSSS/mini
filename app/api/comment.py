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
from app.api.user import user_info


def appendUserInfo(getJson):
    """
    用于在获取评论列表的返回数据中附上用户信息的装饰器，
    装饰CommentProxy.query方法用
    """
    @wraps(getJson)
    def __doAppendImage(self, args):
        ret = getJson(self, args)
        for item in ret:
            userInfo = user_info(item['commentatorID'])
            if userInfo['status']:
                item['userInfo'] = {
                    'userNmae': userInfo['data']['username'],
                    'nickName': userInfo['data']['nickname'],
                    'id': userInfo['data']['id']
                }
            else:
                item['userInfo'] = None
        return ret

    return __doAppendImage


def model2Json(getAll):
    """
    用于装饰CommentProxy.query方法用的装饰器，
    将查询结果从模型对象转换为Json格式的数据
    """
    @wraps(getAll)
    def __doToJson(self, args):
        ret = getAll(self, args)
        proxy = __makeCommentProxy()
        return [proxy.toJson(item) for item in ret]

    return __doToJson


def getAll(qurey):
    """
    用于装饰CommentProxy.query的装饰器，取出查询对象中的所有结果
    """
    @wraps(qurey)
    def __doGetAll(self, args):
        return qurey(self, args).all()

    return __doGetAll


def limitAndStartAddtion(qurey):
    """
    用于装饰CommentProxy.query的装饰器，可以增加对'limit'和'start'
    参数的支持
    """
    @wraps(qurey)
    def __doLimitAndStart(self, args):
        ret = qurey(self, args)
        start = 0
        limit = 50

        if 'start' in args:
            start = args['start']
        if 'limit' in args:
            limit = args['limit']

        return ret.offset(start).limit(limit)

    return __doLimitAndStart


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
        self._filerDict = {}
        self._fileds = fileds
        self.__Comment = Comment

    def __getattr__(self, item):
        def _feedBack(filterx):
            self._filerDict[item] = filterx
            return self

        return _feedBack

    @property
    def Comment(self):
        return self.__Comment

    @Comment.setter
    def setComment(self, _comment):
        self.__Comment = _comment

    def toJson(self, model):
        """
        将模型对象转换成为字典对象
        :param model  [Comment]:
            需要被转换的模型对象
        :return  [dict]:
            转换后的字典对象，该字典的key是模型对象的属性名,
            value 是模型对象的属性值
        """
        jsonDict = {}
        for filed in self._fileds:
            jsonDict[filed] = model.__getattribute__(filed)
        return jsonDict

    def filterArgs(self, args):
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
    def makeRetJson(status=0, messages='', data={}):
        return jsonify({'status': status, 'messages': messages, 'data': data})

    @appendUserInfo
    @model2Json
    @getAll
    @limitAndStartAddtion
    def query(self, args=None):
        """
        查询函数，通过输入的查询条件查询符合条件的模型
        :param args [dict]:
            
        :return:
        """
        if not args:
            return self.Comment.query.filter_by(status=0)

        self._filerDict = self.filterArgs(args)
        self._filerDict['status'] = 0  # 这里假设了表的结构，依赖于表的结构，需要重构
        ret = self.Comment.query.filter_by(**self._filerDict)
        return ret

    def insert(self, args, isVailed=None):
        message = None
        if isVailed and not isVailed(args):
            return self.makeRetJson(0, 'invailed arguments')

        args = self.filterArgs(args)
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
            return self.makeRetJson(0, 'arguments error')
        return self.makeRetJson(1, message)

    def delete(self, args):
        self._filerDict = self.filterArgs(args)
        if len(self._filerDict) <= 0:
            return self.makeRetJson(0, '0 comments have been deleted')
        self._filerDict['status'] = 0
        ret = self.Comment.query.filter_by(**self._filerDict).update({'status': 1})
        return self.makeRetJson(1, str(ret) + ' comments have been deleted')


def __makeCommentProxy():
    if hasattr(__makeCommentProxy, 'proxy'):
        return __makeCommentProxy.proxy
    table_structs = app.config.get('COMMENT_TABLE_STRUCTS')
    table_structs = copy.deepcopy(table_structs)
    table_structs.pop('__tablename__')
    proxy = CommentProxy([key for key, value in table_structs.items()])
    setattr(__makeCommentProxy, 'proxy', proxy)
    return proxy


@api.route(app.config.get('COMMENT_GET_URL'),
           methods=app.config.get('COMMENT_GET_METHODS'))
def getComment():
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
    proxy = __makeCommentProxy()
    args = request.args
    ret = proxy.query(args)
    return proxy.makeRetJson(1, data={'comments': ret})


@api.route(app.config.get('COMMENT_ADD_URL'),
           methods=app.config.get('COMMENT_ADD_METHODS'))
def addComment():
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
    proxy = __makeCommentProxy()
    args = request.args
    return proxy.insert(args)


@api.route(app.config.get('COMMENT_DELETE_URL'),
           methods=app.config.get('COMMENT_DELETE_METHODS'))
def deleteComment():
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
    proxy = __makeCommentProxy()
    args = request.args
    return proxy.delete(args)
