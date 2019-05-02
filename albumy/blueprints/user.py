from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user, fresh_login_required

from ..decorators import confirm_required, permission_required
from ..emails import send_change_email
from ..extensions import db, avatars
from ..forms.user import EditProfileForm, UploadAvatarForm, CropAvatarForm, ChangePasswordForm, ChangeEmailForm, \
    NotificationSettingForm, PrivacySettingForm, DeleteAccountForm
from ..models import User, Photo, Collect
from ..notifications import push_follow_notification
from ..settings import Operations
from ..utils import redirect_back, flash_errors, generate_token, validate_token

user_bp = Blueprint('user', __name__)


@user_bp.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Photo.query.with_parent(user).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items
    return render_template('user/index.html', user=user, pagination=pagination, photos=photos)


@user_bp.route('/<username>/collections')
def show_collections(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    pagination = Collect.query.with_parent(user).order_by(Collect.timestamp.desc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('user/collections.html', user=user, pagination=pagination, collects=collects)


@user_bp.route('/follow/<username>', methods=['POST'])
@login_required
@confirm_required
@permission_required('FOLLOW')
def follow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        flash('重复操作, 以关注该用户', 'info')
        return redirect(url_for('.index', username=username))
    current_user.follow(user)
    db.session.commit()
    if user.receive_follow_notification:
        push_follow_notification(current_user, user)
    flash('关注成功', 'success')
    return redirect_back()


@user_bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        flash('操作失败, 未关注该用户', 'info')
        return redirect(url_for('.index', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('取消关注成功', 'success')
    return redirect_back()


@user_bp.route('/<username>/followers')
@login_required
def show_followers(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_USER_PER_PAGE']
    pagination = user.followers.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/followers.html', user=user, pagination=pagination, follows=follows)


@user_bp.route('/<username>/following')
@login_required
def show_following(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_USER_PER_PAGE']
    pagination = user.following.paginate(page, per_page)
    follows = pagination.items
    return render_template('user/followings.html', user=user, pagination=pagination, follows=follows)


@user_bp.route('/user/settings/profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.username = form.username.data
        current_user.website = form.website.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.commit()
        flash('用户信息已更新', 'success')
        return redirect(url_for('.index', username=current_user.username))
    form.name.data = current_user.name
    form.username.data = current_user.username
    form.website.data = current_user.website
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('user/settings/edit_profile.html', form=form)


@user_bp.route('/settings/avatar')
@login_required
@confirm_required
def change_avatar():
    upload_form = UploadAvatarForm()
    crop_from = CropAvatarForm()
    return render_template('user/settings/change_avatar.html', upload_form=upload_form, crop_from=crop_from)


@user_bp.route('/settings/avatar/upload', methods=['POST'])
@login_required
@confirm_required
def upload_avatar():
    form = UploadAvatarForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = avatars.save_avatar(image)
        current_user.avatar_raw = filename
        db.session.commit()
        flash('头像上传成功', 'success')
    flash_errors(form)
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/avatar/crop', methods=['POST'])
@login_required
@confirm_required
def crop_avatar():
    form = CropAvatarForm()
    if form.validate_on_submit():
        x = form.x.data
        y = form.y.data
        w = form.w.data
        h = form.h.data
        filenames = avatars.crop_avatar(current_user.avatar_raw, x, y, w, h)
        current_user.avatar_s = filenames[0]
        current_user.avatar_m = filenames[1]
        current_user.avatar_l = filenames[2]
        db.session.commit()
        flash('头像已保存', 'success')
        return redirect(url_for('.index', username=current_user.username))
    flash_errors(form)
    return redirect(url_for('.change_avatar'))


@user_bp.route('/settings/change-password', methods=['GET', 'POST'])
@fresh_login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit() and current_user.validate_password(form.old_password.data):
        current_user.password = form.password1.data
        # user = current_user._get_current_object()
        # user.password = form.password1.data
        db.session.commit()
        flash('密码修改成功.', 'success')
        return redirect(url_for('.index', username=current_user.username))
    return render_template('user/settings/change_password.html', form=form)


@user_bp.route('/settings/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        token = generate_token(current_user, Operations.CHANGE_EMAIL, new_email=form.email.data)
        send_change_email(current_user, token)
        flash('验证邮箱以发送, 请注意查收.', 'success')
        return redirect(url_for('.index', username=current_user.username))
    return render_template('user/settings/change_email.html', form=form)


@user_bp.route('/change-email/<token>')
@login_required
def change_email(token):
    if validate_token(token, current_user, Operations.CHANGE_EMAIL):
        flash('邮箱修改成功', 'success')
        return redirect(url_for('.index', username=current_user.username))
    else:
        flash('链接失效, 请重新设置', 'danger')
        return redirect(url_for('.change_email_request'))


@user_bp.route('/settings/notification', methods=['GET', 'POST'])
@login_required
def notification_setting():
    form = NotificationSettingForm()
    if form.validate_on_submit():
        current_user.receive_collect_notification = form.receive_collect_notification.data
        current_user.receive_follow_notification = form.receive_follow_notification.data
        current_user.receive_comment_notification = form.receive_comment_notification.data
        db.session.commit()
        flash('消息提醒设置保存成功', 'success')
        return redirect(url_for('.index', username=current_user.username))
    form.receive_comment_notification.data = current_user.receive_comment_notification
    form.receive_follow_notification.data = current_user.receive_follow_notification
    form.receive_collect_notification.data = current_user.receive_collect_notification
    return render_template('user/settings/edit_notification.html', form=form)


@user_bp.route('/settings/privacy', methods=['GET', 'POST'])
@login_required
def privacy_setting():
    form = PrivacySettingForm()
    if form.validate_on_submit():
        current_user.public_collections = form.public_collections.data
        db.session.commit()
        flash('隐私设置保存成功', 'success')
        return redirect(url_for('.index', username=current_user.username))
    form.public_collections.data = current_user.public_collections
    return render_template('user/settings/edit_privacy.html', form=form)


@user_bp.route('/settings/account/delete', methods=['GET', 'POST'])
@fresh_login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        db.session.delete(current_user._get_current_object())
        db.session.commit()
        flash('你自由啦, 哈哈哈! 再见', 'success')
        return redirect(url_for('main.index'))
    return render_template('user/settings/delete_account.html', form=form)