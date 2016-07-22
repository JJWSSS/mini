# coding=utf-8
from app.api import api
from app.models import Comment
from flask import request
from flask import jsonify
from manage import app
import copy
from app import db


class CommentProxy:
    def __init__(self, fileds):
        self._filerDict = {}
        self._fileds = fileds

    def getFileds(self):
        return self._fileds

    def __getattr__(self, item):
        def _feedBack(filterx):
            self._filerDict[item] = filterx
            return self
        return _feedBack

    def __toJson(self, model):
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

    def query(self, args=None):
        if args is None:
            return Comment.query.all()

        start = 0
        limit = 50
        self._filerDict = self.filterArgs(args, self._fileds)
        if 'start' in args:
            start = args['start']
        if 'limit' in args:
            limit = args['limit']
        ret = Comment.query.filter_by(**self._filerDict).offset(start).limit(limit).all()
        return [self.__toJson(item) for item in ret]

    def insert(self, args, isVailed = None):
        if isVailed and not isVailed(args):
                return jsonify({'status': 'error', 'note': 'invailed arguments'})

        args = self.filterArgs(args, self._fileds)
        db.session.add(Comment(**args))
        exp = None
        try:
            db.session.commit()
        except Exception as e:
            exp = e
            db.session.rollback()
        if exp:
            return jsonify({'status':'error'})
        return jsonify({'status': 'ok'})

    def delete(self, args):
        pass


def __makeCommentProxy():
    if hasattr(__makeCommentProxy, 'proxy'):
        return __makeCommentProxy.proxy

    table_struct = app.config.get('COMMENT_TABLE_STRUCTS')
    table_struct = copy.deepcopy(table_struct)
    table_struct.pop('__tablename__')
    proxy = CommentProxy([key for key, value in table_struct.items()])
    setattr(__makeCommentProxy, 'proxy', proxy)
    return proxy


def getComment():
    proxy = __makeCommentProxy()
    args = request.args
    return jsonify({'comments': proxy.query(args)})

def addComment():
    proxy = __makeCommentProxy()
    args = request.args
    return proxy.insert(args)


# 在这里注册路由
api.route(app.config.get('COMMENT_ADD_URL'))(addComment)
api.route(app.config.get('COMMENT_GET_URL'))(getComment)