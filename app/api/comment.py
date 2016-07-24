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


def appendUserInfo(getJson):
    @wraps(getJson)
    def __doAppendImage(self, args):
        ret = getJson(self, args)
        for item in ret:
            item['UserInfo'] = \
                {'name': 'Lee', 'Time': '2016-07-24', 'Image': 'wow.jpg'}
        return ret

    return __doAppendImage


def model2Json(getAll):
    @wraps(getAll)
    def __doToJson(self, args):
        ret = getAll(self, args)
        proxy = __makeCommentProxy()
        return [proxy.toJson(item) for item in ret]

    return __doToJson


def getAll(qurey):
    @wraps(qurey)
    def __doGetAll(self, args):
        return qurey(self, args).all()

    return __doGetAll


def limitAndStartAddtion(qurey):
    @wraps(qurey)
    def __doLimitAndStart(self, args):
        ret = qurey(self, args)
        start = 0;
        limit = 50;

        if 'start' in args:
            start = args['start']
        if 'limit' in args:
            limit = args['limit']

        return ret.offset(start).limit(limit)

    return __doLimitAndStart


class CommentProxy:
    def __init__(self, fileds):
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
        jsonDict = {}
        for filed in self._fileds:
            jsonDict[filed] = model.__getattribute__(filed)
        return jsonDict

    @staticmethod
    def filterArgs(args, filerFiled):
        ret = {}
        if args is not None:
            for key, value in args.items():
                if key in filerFiled:
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
        if not args:
            return self.Comment.query.filter_by(status=0)

        self._filerDict = self.filterArgs(args, self._fileds)
        self._filerDict['status'] = 0  # 这里假设了表的结构，依赖于表的结构，需要重构
        ret = self.Comment.query.filter_by(**self._filerDict)
        return ret

    def insert(self, args, isVailed=None):
        message = None
        if isVailed and not isVailed(args):
            return self.makeRetJson(0, 'invailed arguments')

        args = self.filterArgs(args, self._fileds)
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
        self._filerDict = self.filterArgs(args, self._fileds)
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
    proxy = __makeCommentProxy()
    args = request.args
    ret = proxy.query(args)
    return proxy.makeRetJson(1,
                             data={'comments': ret})


@api.route(app.config.get('COMMENT_ADD_URL'),
           methods=app.config.get('COMMENT_ADD_METHODS'))
def addComment():
    proxy = __makeCommentProxy()
    args = request.args
    return proxy.insert(args)


@api.route(app.config.get('COMMENT_DELETE_URL'),
           methods=app.config.get('COMMENT_DELETE_METHODS'))
def deleteComment():
    proxy = __makeCommentProxy()
    args = request.args
    return proxy.delete(args)
