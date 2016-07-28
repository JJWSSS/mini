from functools import wraps
from app.api import user
from flask import request
from flask_login import current_user
from flask import jsonify


# bug 封印，此封印可以将 '插入一条无goodsID无commentatorID的评论' 之bug 封印
# 用法：作为装饰器装饰CommentProxy.insert方法
# 2016-07-28 brooksli
def check_args_for_insert(insertor):
    @wraps(insertor)
    def __do_check(self, args):
        for item in ['context', 'goodsID', 'commentatorID']:
            if not (item in args):
                return self.make_ret_json(0, 'argusments error')
        return insertor(self, args)

    return __do_check


def append_user_info(get_json):
    """
    用于在获取评论列表的返回数据中附上用户信息的装饰器，
    装饰CommentProxy.query方法用
    """

    @wraps(get_json)
    def __do_append_image(self, **args):
        ret = get_json(self, args)
        for item in ret:
            user_info = user.user_info(item['commentatorID'])
            if user_info['status']:
                item['userInfo'] = {
                    'userNmae': user_info['data']['username'],
                    'nickName': user_info['data']['nickname'],
                    'id': user_info['data']['id'],
                    'picture': user_info['data']['picture'],
                    'compressPicture': user_info['data']['compressPicture']
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
        from app.api.comment import make_comment_proxy
        ret = get_all(self, args)
        proxy = make_comment_proxy()
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
        if args:
            if 'start' in args:
                start = args['start']
            if 'limit' in args:
                limit = args['limit']

        return ret.offset(start).limit(limit)
    return __do_limit_and_start


def check_commentator_for_add_comment(add_comment_func):
    from app.api.comment import make_comment_proxy

    @wraps(add_comment_func)
    def __do_check():
        proxy = make_comment_proxy()
        args = request.json
        if args is None:
            return jsonify(proxy.make_ret_json(0, 'arguments error'))
        if 'commentatorID' not in args:
            if hasattr(current_user, 'userID'):
                args['commentatorID'] = current_user.userID
                add_comment_func()
            else:
                ret = proxy.make_ret_json(0, 'The current user does not have a userID')
                return jsonify(ret)
    return __do_check
