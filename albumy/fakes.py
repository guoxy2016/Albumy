from faker import Faker
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import User

fake = Faker('zh_CN')


def fake_admin():
    admin = User(
        name='张三丰',
        email='guoxy_mail0122@qq.com',
        username='admin',
        website='http://www.example.com',
        bio=fake.sentence(),
        confirmed=True
    )
    admin.password = '12345678'
    db.session.add(admin)
    db.session.commit()


def fake_users(count=10):
    for i in range(count):
        user = User(
            name=fake.name(),
            email=fake.email(),
            username=fake.user_name(),
            website=fake.url(),
            bio=fake.sentence(),
            location=fake.city(),
            member_since=fake.data_this_decade(),
            confirmed=True
        )
        user.password = '12345678'
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()