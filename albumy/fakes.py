import os
import random

from PIL import Image
from faker import Faker
from flask import current_app
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import User, Photo, Tag, Comment

fake = Faker('zh_CN')


def fake_admin():
    admin = User(
        name='Guoxy2016',
        email=os.getenv('ALBUMY_ADMIN', 'admin@helloflask.com'),
        username='guoxy2016',
        website='https://github.com/guoxy2016',
        bio='python python',
        location='北京',
        confirmed=True
    )
    admin.password = '12345678'
    db.session.add(admin)
    db.session.commit()


def fake_users(count=6):
    for i in range(count):
        user = User(
            name=fake.name(),
            email=fake.email(),
            username=fake.user_name(),
            website=fake.url(),
            bio=fake.sentence(),
            location=fake.city(),
            member_since=fake.date_this_decade(),
            confirmed=True
        )
        user.password = '12345678'
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_photos(count=30):
    upload_path = current_app.config['ALBUMY_UPLOAD_PATH']
    for i in range(count):
        filename = 'random_%s.jpg' % i
        r = lambda: random.randint(10, 255)
        img = Image.new('RGB', (800, 800), (r(), r(), r()))
        img.save(os.path.join(upload_path, filename))
        photo = Photo(
            filename=filename,
            filename_m=filename,
            filename_s=filename,
            description=fake.text(),
            timestamp=fake.date_time_this_year()
        )
        count_user = User.query.count()
        count_tag = Tag.query.count()
        photo.author = User.query.get(random.randint(1, count_user))
        for j in range(random.randint(1, 5)):
            tag = Tag.query.get(random.randint(1, count_tag))
            if tag not in photo.tags:
                photo.tags.append(tag)
        db.session.add(photo)
        db.session.commit()


def fake_tags(count=20):
    for i in range(count):
        tag = Tag(name=fake.word())
        db.session.add(tag)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_comments(count=100):
    for i in range(count):
        comment = Comment(
            body=fake.sentence(),
            timestamp=fake.date_time_this_year()
        )
        comment.photo = Photo.query.get(random.randint(1, Photo.query.count()))
        comment.author = User.query.get(random.randint(1, User.query.count()))
        db.session.add(comment)
    db.session.commit()


def fake_collects(count=50):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.collect(Photo.query.get(random.randint(1, Photo.query.count())))
        db.session.commit()


def fake_follow(count=20):
    for i in range(count):
        user = User.query.get(random.randint(1, User.query.count()))
        user.follow(User.query.get(random.randint(1, User.query.count())))
    db.session.commit()
