from flask import url_for

from albumy.models import User
from albumy.settings import Operations
from albumy.utils import generate_token
from .base import BaseTestCase


class AuthTestCase(BaseTestCase):

    def test_register_account(self):
        response = self.client.get(url_for('auth.register'))
        self.assertIn('欢迎加入', response.get_data(as_text=True))
        response = self.client.post(url_for('auth.register'), data=dict(
            name='zhangsan',
            email='test@helloflask.com',
            username='test',
            password='12345678',
            password2='12345678'
        ), follow_redirects=True)
        self.assertIn('验证邮件已发送, 请注意查收.', response.get_data(as_text=True))

    def test_login_user(self):
        response = self.login()
        data = response.get_data(as_text=True)
        self.assertIn('欢迎回来', data)

        self.login(email='locked@helloflask.com', password='12345678')
        response = self.client.get(url_for('user.index', username='locked_user'))
        data = response.get_data(as_text=True)
        self.assertIn('该帐户被锁定了', data)
        self.logout()

        response = self.login(email='block@helloflask.com', password='12345678')
        data = response.get_data(as_text=True)
        self.assertIn('帐户被封禁了', data)
        self.logout()

        response = self.login(email='wrong-username@helloflask.com', password='wrong-password')
        data = response.get_data(as_text=True)
        self.assertIn('用户名或密码错误', data)
        self.logout()

    def test_logout_user(self):
        self.login()
        response = self.logout()
        data = response.get_data(as_text=True)
        self.assertIn('退出成功', data)

    def test_login_protect(self):
        response = self.client.get(url_for('main.upload'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先登陆', data)

    def test_unconfirmed_user_permission(self):
        self.login(email='unconfirm@helloflask.com', password='12345678')
        response = self.client.get(url_for('main.upload'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('请先验证您的邮件', data)

    def test_locked_user_permission(self):
        self.login(email='locked@helloflask.com', password='12345678')
        response = self.client.get(url_for('main.upload'), follow_redirects=True)
        self.assertEqual(response.status_code, 403)

    def test_confirm_account(self):
        user = User.query.filter_by(email='unconfirm@helloflask.com').first()
        self.assertFalse(user.confirmed)
        token = generate_token(user=user, operation='confirm')
        self.login(email='unconfirm@helloflask.com', password='12345678')
        response = self.client.get(url_for('auth.confirm', token=token), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('您的账户以验证', data)
        self.assertTrue(user.confirmed)

    def test_bad_confirm_token(self):
        self.login(email='unconfirm@helloflask.com', password='12345678')
        response = self.client.get(url_for('auth.confirm', token='bad token'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('您的验证信息已过期', data)
        self.assertNotIn('您的账户以验证', data)

    def test_reset_password(self):
        response = self.client.post(url_for('auth.forget_password'), data=dict(
            email='normal@helloflask.com',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('邮件已发送请注意查收', data)
        user = User.query.filter_by(email='normal@helloflask.com').first()
        self.assertTrue(user.validate_password('12345678'))

        token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
        response = self.client.post(url_for('auth.reset_password', token=token), data=dict(
            email='normal@helloflask.com',
            password='new-password',
            password2='new-password'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('修改密码成功', data)
        self.assertTrue(user.validate_password('new-password'))
        self.assertFalse(user.validate_password('12345678'))

        # bad token
        response = self.client.post(url_for('auth.reset_password', token='bad token'), data=dict(
            email='normal@helloflask.com',
            password='new-password',
            password2='new-password'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('令牌失效, 重新发送验证邮件', data)
        self.assertNotIn('修改密码成功', data)
