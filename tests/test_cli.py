from albumy.models import db, User, Photo, Tag, Comment, Follow
from .base import BaseTestCase


class CliTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(CliTestCase, self).setUp()
        db.drop_all()

    def test_cli_init_db(self):
        result = self.runner.invoke(args=['init-db'])
        self.assertIn('create all', result.output)

        result = self.runner.invoke(args=['init-db', '--drop'], input='y\n')
        self.assertIn('All data well be deleted, are you sure', result.output)
        self.assertIn('drop done', result.output)
        self.assertIn('create all', result.output)

    def test_cli_init(self):
        result = self.runner.invoke(args=['init'])
        self.assertIn('Initializing the database', result.output)
        self.assertIn('Initializing the roles and permissions', result.output)
        self.assertIn('Done', result.output)

    def test_cli_create_superuser(self):
        db.create_all()
        result = self.runner.invoke(args=['create-superuser', '-e', '12345678@qq.com', '-p', '12345678'])
        self.assertIn('请先执行 flask init', result.output)
        self.assertNotIn('正在创建超级用户', result.output)
        self.assertNotIn('完成', result.output)

        self.runner.invoke(args=['init'])
        result = self.runner.invoke(args=['create-superuser', '-e', '12345678qq.com', '-p', '12345678'])
        self.assertIn('邮箱的格式不正确', result.output)
        self.assertNotIn('正在创建超级用户', result.output)
        self.assertNotIn('完成', result.output)

        result = self.runner.invoke(args=['create-superuser', '-e', '12345678@qq.com', '-p', '123'])
        self.assertIn('密码的长度范围是8-128', result.output)
        self.assertNotIn('正在创建超级用户', result.output)
        self.assertNotIn('完成', result.output)

        result = self.runner.invoke(args=['create-superuser', '-e', '12345678@qq.com', '-p', '12345678'])
        self.assertIn('正在创建超级用户', result.output)
        self.assertIn('完成', result.output)

        result = self.runner.invoke(args=['create-superuser', '-e', '12345678@qq.com', '-p', '11111111'])
        self.assertIn('更改用户', result.output)
        self.assertIn('完成', result.output)

        self.assertEqual(User.query.count(), 1)

    def test_cli_forge(self):
        result = self.runner.invoke(args=['forge'])
        self.assertIn('Initializing the roles and permissions', result.output)
        self.assertIn('Generating Administrator', result.output)
        self.assertIn('Generating 6 users', result.output)
        self.assertIn('Generating 20 tags', result.output)
        self.assertIn('Generating 30 photos', result.output)
        self.assertIn('Generating 100 comments', result.output)
        self.assertIn('Generating 50 collects', result.output)
        self.assertIn('Generating 20 follows', result.output)
        self.assertIn('Done', result.output)
        self.assertEqual(User.query.count(), 6 + 1)
        self.assertEqual(Photo.query.count(), 30)
        self.assertEqual(Tag.query.count(), 20)
        self.assertEqual(Comment.query.count(), 100)
        self.assertLessEqual(Follow.query.count(), 20 + 6 + 1)

        result = self.runner.invoke(args=['forge', '--user', '10'])
        self.assertIn('Generating 10 users', result.output)
        self.assertEqual(User.query.count(), 10 + 1)

        result = self.runner.invoke(args=['forge', '--photo', '3'])
        self.assertIn('Generating 3 photos', result.output)
        self.assertEqual(Photo.query.count(), 3)

        result = self.runner.invoke(args=['forge', '--tag', '11'])
        self.assertIn('Generating 11 tags', result.output)
        self.assertEqual(Tag.query.count(), 11)

        result = self.runner.invoke(args=['forge', '--comment', '12'])
        self.assertIn('Generating 12 comments', result.output)
        self.assertEqual(Comment.query.count(), 12)

        result = self.runner.invoke(args=['forge', '--follow', '13'])
        self.assertIn('Generating 13 follows', result.output)
        self.assertLessEqual(Follow.query.count(), 13 + 6 + 1)
