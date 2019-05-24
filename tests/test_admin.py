from flask import url_for

from albumy.models import User, Role, Tag
from .base import BaseTestCase


class AdminTestCase(BaseTestCase):

    def setUp(self) -> None:
        super(AdminTestCase, self).setUp()
        self.login('admin@helloflask.com', '12345678')

    def test_bad_permission(self):
        self.logout()
        response = self.client.get(url_for('admin.index'), follow_redirects=True)
        self.assertIn('请先登陆', response.get_data(as_text=True))

        self.login()
        response = self.client.get(url_for('admin.index'), follow_redirects=True)
        self.assertIn('Forbidden', response.get_data(as_text=True))

    def test_lock_user(self):
        response = self.client.post(url_for('admin.lock_user', user_id=2), follow_redirects=True)
        self.assertIn('用户被锁定', response.get_data(as_text=True))

        user = User.query.get(2)
        self.assertEqual(user.role.name, 'Locked')

        response = self.client.post(url_for('admin.lock_user', user_id=1), follow_redirects=True)
        self.assertIn('Forbidden', response.get_data(as_text=True))

    def test_unlock_user(self):
        response = self.client.post(url_for('admin.unlock_user', user_id=4), follow_redirects=True)
        self.assertIn('用户已解锁', response.get_data(as_text=True))
        user = User.query.get(4)
        self.assertEqual(user.role.name, 'Normal')

    def test_block_user(self):
        response = self.client.post(url_for('admin.block_user', user_id=2), follow_redirects=True)
        self.assertIn('用户被封禁', response.get_data(as_text=True))

        user = User.query.get(2)
        self.assertFalse(user.is_active)

        response = self.client.post(url_for('admin.block_user', user_id=1), follow_redirects=True)
        self.assertIn('Forbidden', response.get_data(as_text=True))

    def test_unblock_user(self):
        response = self.client.post(url_for('admin.unblock_user', user_id=5), follow_redirects=True)
        self.assertIn('用户已解封', response.get_data(as_text=True))
        user = User.query.get(2)
        self.assertTrue(user.is_active)

    def test_edit_profile_admin(self):
        response = self.client.get(url_for('admin.edit_profile_admin', user_id=2))
        data = response.get_data(as_text=True)
        self.assertIn('资料编辑', data)
        self.assertIn('normal@helloflask.com', data)
        self.assertIn('Normal', data)
        self.assertIn('normal_user', data)

        role_id = Role.query.filter_by(name='Locked').first().id
        self.client.post(url_for('admin.edit_profile_admin', user_id=2), data=dict(
            name='User_test',
            bio='blah...',
            location='浙江',
            username='zhangsan',
            email='test@helloflask.com',
            role=role_id,
            active=True,
            website='http://www.test.com',
            confirmed=True
        ), follow_redirects=True)
        user = User.query.get(2)
        self.assertEqual(user.name, 'User_test')
        self.assertEqual(user.bio, 'blah...')
        self.assertEqual(user.location, '浙江')
        self.assertEqual(user.username, 'zhangsan')
        self.assertEqual(user.email, 'test@helloflask.com')
        self.assertEqual(user.role.name, 'Locked')
        self.assertTrue(user.active)
        self.assertEqual(user.website, 'http://www.test.com')
        self.assertTrue(user.confirmed)

    def test_delete_tag(self):
        response = self.client.get(url_for('admin.delete_tag', tag_id=1), follow_redirects=True)
        self.assertIn('Method Not Allowed', response.get_data(as_text=True))
        response = self.client.post(url_for('admin.delete_tag', tag_id=1), follow_redirects=True)
        self.assertIn('标签删除成功', response.get_data(as_text=True))
        self.assertIsNone(Tag.query.get(1))

    def test_index(self):
        response = self.client.get(url_for('admin.index'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('控制面板主页', data)
        self.assertIn('图片', data)
        self.assertIn('用户', data)
        self.assertIn('评论', data)
        self.assertIn('标签', data)

    def test_manage_photo(self):
        response = self.client.get(url_for('admin.manage_photo'))
        self.assertIn('举报数量', response.get_data(as_text=True))
        self.assertIn('图片', response.get_data(as_text=True))
        self.assertIn('test_s.jpg', response.get_data(as_text=True))
        self.assertIn('test2_s.jpg', response.get_data(as_text=True))

        response = self.client.get(url_for('admin.manage_photo', order='by_time'))
        self.assertIn('上传时间', response.get_data(as_text=True))

    def test_manage_user(self):
        response = self.client.get(url_for('admin.manage_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal', data)
        self.assertIn('Administrator', data)
        self.assertIn('Locked', data)
        self.assertIn('guoxy2016', data)
        self.assertIn('normal_user', data)
        self.assertIn('unconfirm_user', data)
        self.assertIn('locked_user', data)
        self.assertIn('block_user', data)

        response = self.client.get(url_for('admin.manage_user', filter='locked'))
        data = response.get_data(as_text=True)
        self.assertIn('Locked', data)
        self.assertNotIn('Administrator', data)
        self.assertNotIn('Normal', data)
        self.assertIn('解锁', data)

        response = self.client.get(url_for('admin.manage_user', filter='blocked'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal', data)
        self.assertIn('解封', data)
        self.assertNotIn('Administrator', data)
        self.assertNotIn('Locked', data)

        response = self.client.get(url_for('admin.manage_user', filter='administrator'))
        data = response.get_data(as_text=True)
        self.assertIn('Administrator', data)
        self.assertNotIn('Normal', data)
        self.assertNotIn('Locked', data)
        self.assertNotIn('Moderator', data)

        response = self.client.get(url_for('admin.manage_user', filter='moderator'))
        data = response.get_data(as_text=True)
        self.assertNotIn('Administrator', data)
        self.assertNotIn('Normal', data)
        self.assertNotIn('Locked', data)

    def test_manage_tag(self):
        response = self.client.get(url_for('admin.manage_tag'))
        self.assertIn('test tag', response.get_data(as_text=True))

    def test_manage_comment(self):
        response = self.client.get(url_for('admin.manage_comment'))
        self.assertIn('举报数量', response.get_data(as_text=True))
        self.assertIn('test comment body', response.get_data(as_text=True))
        response = self.client.get(url_for('admin.manage_comment', order='by_time'))
        self.assertIn('评论时间', response.get_data(as_text=True))
