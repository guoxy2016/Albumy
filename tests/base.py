from unittest import TestCase

from flask import url_for

from albumy import create_app
from albumy.extensions import db
from albumy.models import Role, User, Photo, Comment, Tag


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        Role.init_role()

        admin_user = User(email='admin@helloflask.com', name='Admin', username='guoxy2016', confirmed=True)
        admin_user.password = '12345678'

        normal_user = User(email='normal@helloflask.com', name='Normal', username='normal_user', confirmed=True)
        normal_user.password = '12345678'

        unconfirm_user = User(email='unconfirm@helloflask.com', name='Unconfirm', username='unconfirm_user',
                              confirmed=False)
        unconfirm_user.password = '12345678'

        locked_user = User(email='locked@helloflask.com', name='Locked', username='locked_user', confirmed=True,
                           locked=True)
        locked_role = Role.query.filter_by(name='Locked').first()
        locked_user.role = locked_role
        locked_user.password = '12345678'

        block_user = User(email='block@helloflask.com', name='Block', username='block_user', confirmed=True,
                          active=False)
        block_user.password = '12345678'

        photo = Photo(filename='test.jpg', filename_s='test_s.jpg', filename_m='test_m.jpg', author=admin_user,
                      description='Photo 1')
        photo2 = Photo(filename='test2.jpg', filename_s='test2_s.jpg', filename_m='test2_m.jpg', author=normal_user,
                       description='Photo 2')

        comment = Comment(body='test comment body', photo=photo, author=normal_user)
        tag = Tag(name='test tag')
        photo.tags.append(tag)
        db.session.add_all(
            [admin_user, normal_user, unconfirm_user, locked_user, block_user, photo, photo2, comment, tag])
        db.session.commit()

    def tearDown(self) -> None:
        db.drop_all()
        self.context.pop()

    def login(self, email='normal@helloflask.com', password='12345678'):
        return self.client.post(url_for('auth.login'), data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
