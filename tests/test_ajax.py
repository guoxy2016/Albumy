from flask import url_for

from albumy.models import User, Photo
from .base import BaseTestCase


class AjaxTestCase(BaseTestCase):
    def setUp(self) -> None:
        super(AjaxTestCase, self).setUp()
        self.login()

    def test_get_profile(self):
        response = self.client.get(url_for('ajax.get_profile', user_id=1))
        self.assertIn('guoxy2016', response.get_data(as_text=True))
    
    def test_follow(self):
        response = self.client.post(url_for('ajax.follow', username='guoxy2016'))
        self.assertEqual('已关注用户', response.get_json().get('message'))
        response = self.client.post(url_for('ajax.follow', username='guoxy2016'))
        self.assertEqual('重复的操作, 以关注用户', response.get_json().get('message'))
        self.logout()
        response = self.client.post(url_for('ajax.follow', username='guoxy2016'))
        self.assertEqual('用户未登录', response.get_json().get('message'))
        self.assertEqual(response.status_code, 401)

        self.login('unconfirm@helloflask.com')
        response = self.client.post(url_for('ajax.follow', username='guoxy2016'))
        self.assertEqual(response.get_json().get('message'), '请验证邮箱后操作')
        self.assertEqual(response.status_code, 400)
        self.logout()
        self.login('locked@helloflask.com')

        user = User.query.get(2)
        admin_user = User.query.get(1)
        self.assertTrue(user.is_following(admin_user))

    def test_unfollow(self):
        response = self.client.post(url_for('ajax.unfollow', username='guoxy2016'))
        self.assertEqual('无效的操作, 您为关注该用户', response.get_json().get('message'))
        self.client.post(url_for('ajax.follow', username='guoxy2016'))
        response = self.client.post(url_for('ajax.unfollow', username='guoxy2016'))
        self.assertEqual('已取消关注', response.get_json().get('message'))
        self.logout()
        response = self.client.post(url_for('ajax.unfollow', username='guoxy2016'))
        self.assertEqual('用户未登录', response.get_json().get('message'))

        user = User.query.get(2)
        admin_user = User.query.get(1)
        self.assertFalse(user.is_following(admin_user))

    def test_followers_count(self):
        response = self.client.get(url_for('ajax.followers_count', user_id=1))
        self.assertEqual(response.get_json().get('count'), 0)

    def test_notifications_count(self):
        response = self.client.get(url_for('ajax.notifications_count'))
        self.assertEqual(response.get_json().get('count'), 0)
        self.logout()
        response = self.client.get(url_for('ajax.notifications_count'))
        self.assertEqual(response.get_json().get('message'), '用户未登录')
        self.assertEqual(response.status_code, 401)

    def test_collect(self):
        response = self.client.get(url_for('ajax.collect', photo_id=1), follow_redirects=True)
        self.assertIn('The method is not allowed for the requested URL', response.get_json().get('message'))
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '收藏图片成功')
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '重复的操作, 用户已收藏.')
        self.assertEqual(response.status_code, 400)

        self.logout()
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '用户未登录')
        self.assertEqual(response.status_code, 401)

        self.login('unconfirm@helloflask.com')
        response = self.client.post(url_for('ajax.collect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '请验证邮箱后操作')
        self.assertEqual(response.status_code, 400)

    def test_uncollect(self):
        self.client.post(url_for('ajax.collect', photo_id=1))
        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '取消收藏成功')

        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '你还没有收藏这张图片')
        self.assertEqual(response.status_code, 400)
        self.logout()
        response = self.client.post(url_for('ajax.uncollect', photo_id=1))
        self.assertEqual(response.get_json().get('message'), '用户未登录')
        self.assertEqual(response.status_code, 401)

    def test_collectors_count(self):
        response = self.client.get(url_for('ajax.collectors_count', photo_id=1))
        self.assertEqual(response.get_json().get('count'), len(Photo.query.get(1).collectors))

