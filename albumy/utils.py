import os
from urllib.parse import urlparse, urljoin

from PIL import Image
from flask import request, redirect, url_for, flash, current_app
from flask_dropzone import random_filename
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

from .extensions import db
from .models import User
from .settings import Operations


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and test_url.netloc == ref_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in (request.args.get('next'), request.referrer):
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(user, operation, expires_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
    data = dict(id=user.id, operation=operation)
    data.update(**kwargs)
    return s.dumps(data).decode()


def validate_token(token, user, operation, password=None):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if data.get('id') != user.id or data.get('operation') != operation:
        return False

    if operation == Operations.CONFIRM:
        user.confirmed = True
    elif operation == Operations.RESET_PASSWORD:
        user.password = password
    elif operation == Operations.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if User.query.filter_by(email=new_email).first() is not None:
            return False
        user.email = new_email
    else:
        return False

    db.session.commit()
    return True


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash('`%s`字段提交时出现错误:%s' % (getattr(form, field).label.text, error), 'danger')


def resize_image(img, filename, base_width):
    filename, ext = os.path.splitext(filename)
    if img.size[0] < base_width:
        return filename + ext
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1])) * float(w_percent))
    img = img.resize((base_width, h_size), Image.ANTIALIAS)
    filename += current_app.config['ALBUMY_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename


def validate_image(fp):
    try:
        filename = random_filename(fp.filename)
        img = Image.open(fp)
        fp.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename))
    except IOError:
        return None
    img_m = img.copy()
    img_s = img.copy()
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename))
    filename_m = resize_image(img_m, filename, current_app.config['ALBUMY_PHOTO_SIZE']['medium'])
    filename_s = resize_image(img_s, filename, current_app.config['ALBUMY_PHOTO_SIZE']['small'])
    return dict(name=filename, name_m=filename_m, name_s=filename_s)


# 初始化内容
def init_user_permission():
    from .models import User, Role
    for user in User.query.all():
        if user.email == current_app.config['ALBUMY_ADMIN_EMAIL']:
            user.role = Role.query.filter_by(name='Administrator').first()
        else:
            user.role = Role.query.filter_by(name='User').first()
        db.session.add(user)
    db.session.commit()


def init_user_avatars():
    from .models import User
    for user in User.query.all():
        user.generate_avatar()
        db.session.add(user)
    db.session.commit()


def init_photo_flag():
    from .models import Photo
    for photo in Photo.query.all():
        photo.flag = 0
        db.session.add(photo)
    db.session.commit()


def follow_self_all():
    from .models import User
    for user in User.query.all():
        user.follow(user)


def init_user_notification():
    from .models import User
    for user in User.query.all():
        user.receive_follow_notification = True
        user.receive_collect_notification = True
        user.receive_comment_notification = True
    db.session.commit()


def init_user_privacy():
    from .models import User
    for user in User.query.all():
        user.public_collections = True
    db.session.commit()


def init_user_active_lock():
    from .models import User
    for user in User.query.all():
        user.active = True
        user.locked = False
    db.session.commit()
