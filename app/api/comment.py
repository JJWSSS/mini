# coding=utf-8
from app.api import api
from app.models import Comment
from flask import request
from flask import jsonify
from manage import app


class CommentProxy:
    def __init__(self, fileds):
        self._filerDict = {}
        self._fileds = fileds

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

    def query(self, args=None):
        if args is not None:
            for key, value in args.items():
                if key in self._fileds:
                    self._filerDict[key] = value
        ret = Comment.query.filter_by(**self._filerDict).all()
        return [self.__toJson(item) for item in ret ]

    def insert(self, args):
        pass

    def delete(self, args):
        pass


def getComment():
    proxy = CommentProxy(app.config.get('COMMENT_TABLE_STRUCTS'))
    args = request.args
    return jsonify({'comments': proxy.query(args)})


# 在这里注册路由
api.route(app.config.get('COMMENT_GET_URL'))(getComment)