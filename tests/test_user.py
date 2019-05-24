import io

from flask import url_for

from albumy.models import User, Photo
from albumy.settings import Operations
from albumy.utils import generate_token
from .base import BaseTestCase


class UserTestCase(BaseTestCase):

    def test_index_page(self):
        response = self.client.get(url_for('user.index', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Normal', data)

        self.login(email='locked@helloflask.com')
        response = self.client.get(url_for('user.index', username='locked_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Locked', data)
        self.assertIn('该帐户被锁定了', data)

    def test_show_collections(self):
        response = self.client.get(url_for('user.show_collections', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('没有收藏', data)

        user = User.query.get(2)
        user.collect(Photo.query.get(1))
        response = self.client.get(url_for('user.show_collections', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertNotIn('没有收藏', data)

    def test_follow(self):
        response = self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登陆', data)

        self.login(email='unconfirm@helloflask.com')
        response = self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先验证您的邮件', data)

        self.logout()

        self.login()
        response = self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('关注成功', data)

        response = self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('重复操作, 已关注该用户', data)

        user = User.query.get(1)
        self.assertEqual(len(user.notifications), 1)

    def test_unfollow(self):
        response = self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登陆', data)

        self.login()
        response = self.client.post(url_for('user.unfollow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('操作失败, 未关注该用户', data)

        self.client.post(url_for('user.follow', username='guoxy2016'), follow_redirects=True)

        response = self.client.post(url_for('user.unfollow', username='guoxy2016'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('取消关注成功', data)

    def test_show_followers(self):
        response = self.client.get(url_for('user.show_followers', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('当前没有人关注你', data)

        user = User.query.get(1)
        user.follow(User.query.get(2))

        response = self.client.get(url_for('user.show_followers', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Admin', data)
        self.assertNotIn('当前没有人关注你', data)

    def test_show_following(self):
        response = self.client.get(url_for('user.show_following', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('当前没有关注任何人', data)

        user = User.query.get(2)
        user.follow(User.query.get(1))

        response = self.client.get(url_for('user.show_following', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Admin', data)
        self.assertNotIn('当前没有关注任何人', data)

    def test_edit_profile(self):
        self.login()
        response = self.client.post(url_for('user.edit_profile'), data=dict(
            username='newname',
            name='New Name',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('用户信息已更新', data)
        user = User.query.get(2)
        self.assertEqual(user.name, 'New Name')
        self.assertEqual(user.username, 'newname')

    def test_change_avatar(self):
        self.login()
        response = self.client.get(url_for('user.change_avatar'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('修改头像', data)

    def test_upload_avatar(self):
        self.login()
        data = {'image': (io.BytesIO(b"abcdef"), 'test.jpg')}
        response = self.client.post(url_for('user.upload_avatar'), data=data, follow_redirects=True,
                                    content_type='multipart/form-data')
        data = response.get_data(as_text=True)
        self.assertIn('头像上传成功', data)

    def test_change_password(self):
        user = User.query.get(2)
        self.assertTrue(user.validate_password('12345678'))

        self.login()
        response = self.client.post(url_for('user.change_password'), data=dict(
            old_password='12345678',
            password1='new-password',
            password2='new-password',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('密码修改成功', data)
        self.assertTrue(user.validate_password('new-password'))
        self.assertFalse(user.validate_password('old-password'))

    def test_change_email(self):
        user = User.query.get(2)
        self.assertEqual(user.email, 'normal@helloflask.com')
        token = generate_token(user=user, operation=Operations.CHANGE_EMAIL, new_email='new@helloflask.com')

        self.login()
        response = self.client.get(url_for('user.change_email', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('邮箱修改成功', data)
        self.assertEqual(user.email, 'new@helloflask.com')

        response = self.client.get(url_for('user.change_email', token='bad'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('链接失效, 请重新设置', data)

    def test_notification_setting(self):
        self.login()
        response = self.client.post(url_for('user.notification_setting'), data=dict(
            receive_collect_notification='',
            receive_comment_notification='',
            receive_follow_notification=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('消息提醒设置保存成功', data)

        user = User.query.get(2)

        self.assertEqual(user.receive_collect_notification, False)
        self.assertEqual(user.receive_comment_notification, False)
        self.assertEqual(user.receive_follow_notification, False)

        self.logout()
        self.login(email='admin@helloflask.com')
        self.client.post(url_for('user.follow', username='normal'))
        self.client.post(url_for('main.new_comment', photo_id=2), data=dict(body='test comment from admin user.'))
        self.client.post(url_for('main.collect', photo_id=2))
        self.assertEqual(len(user.notifications), 0)

    def test_privacy_setting(self):
        self.login()
        response = self.client.post(url_for('user.privacy_setting'), data=dict(
            public_collections='',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('隐私设置保存成功', data)

        user = User.query.get(2)

        self.assertEqual(user.public_collections, False)
        self.logout()
        response = self.client.get(url_for('user.show_collections', username='normal_user'))
        data = response.get_data(as_text=True)
        self.assertIn('当前用户没有公开他的收藏夹', data)

    def test_delete_account(self):
        self.login()
        response = self.client.post(url_for('user.delete_account'), data=dict(
            username='normal_user',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('你自由啦, 哈哈哈! 再见', data)
        self.assertEqual(User.query.get(2), None)
