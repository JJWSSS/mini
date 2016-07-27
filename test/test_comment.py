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

    def testCommentGet_withNoneArgs(self):
        ret = self.proxy.query(None)
        print(ret)
        for item in ret:
            self.assertFalse(item['status'])

    def testCommentGet_with_limit(self):
        for limit_num in range(1, 100):
            ret = self.proxy.query({"limit": limit_num})
            self.assertFalse(len(ret) > limit_num)