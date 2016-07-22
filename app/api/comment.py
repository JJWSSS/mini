# coding=utf-8
from app import db
from app.models import Comment

# 支持操作 ： 1. 根据任意的域进行检索
#            2. 根据relationship的backref进行反查
#            3.
class CommitProxy(Comment):
    def __init__(self, typeMap):
        self._filerDict = dict()
        self.__typeMap = typeMap

    def __getattr__(self, item):
        def _feedBack(filterx):
            self._filerDict[item] = self.__typeMap[item](filterx)
            return self
        return _feedBack

    def query(self):
        return super(CommitProxy, self).query.filter_by(self._filerDict)


if __name__ == '__main__':
    proxy = CommitProxy({'commentID': int, 'goodID': int, 'commentatorID': int, 'context': str, 'status': int})
    proxy.commentID(123).goodID(4516)
    #proxy.query().all()
    print (proxy._filerDict)
