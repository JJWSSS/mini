import unittest
from app import create_app
from app import db
from app.api.comment import CommentProxy
import copy


class CommentAPITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('comment')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.init_app(self.app)
        db.create_all()

        table_structs = self.app.config.get('COMMENT_TABLE_STRUCTS')
        table_structs = copy.deepcopy(table_structs)
        table_structs.pop('__tablename__')
        self.proxy = CommentProxy([key for key, value in table_structs.items()])

    def tearDown(self):
        pass

    def test_comment_get_with_none_args(self):
        ret = self.proxy.query(None)
        for item in ret:
            self.assertFalse(item['status'])

    def test_comment_get_with_limit(self):
        for limit_num in range(1, 100):
            ret = self.proxy.query({"limit": limit_num})
            self.assertFalse(len(ret) > limit_num)

    def test_comment_get_with_start(self):
        ret = self.proxy.query({'start': 0})
        start_id = ret[0]['commentID']

        for start_num in range(0, len(ret) + 100):
            result = self.proxy.query({'start': start_num})
            if start_num < len(ret):
                self.assertTrue(result[0]['commentID'] == (start_id + start_num))
            else:
                self.assertFalse(len(result))

    def test_comment_get_with_goodsID(self):
        all_comments = self.proxy.query({})
        for item in all_comments:
            for goods_item in self.proxy.query({'goodsID': item['goodsID']}):
                self.assertTrue(goods_item['goodsID'] == item['goodsID'])

    def test_comment_get_with_commentatorID(self):
        all_comments = self.proxy.query({})
        for item in all_comments:
            for goods_item in self.proxy.query({'commentatorID': item['commentatorID']}):
                self.assertTrue(goods_item['commentatorID'] == item['commentatorID'])


if __name__ == "__main__":
    # 构造测试集
    suite = unittest.TestSuite()
    suite.addTest(CommentAPITestCase)

    # 执行测试
    runner = unittest.TextTestRunner()
    runner.run(suite)