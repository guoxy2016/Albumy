from flask import Blueprint, flash, abort, render_template, request, current_app
from flask_login import login_required, current_user

from ..decorators import permission_required, admin_required
from ..extensions import db
from ..forms.admin import EditProfileAdminForm
from ..models import User, Role, Tag, Photo, Comment
from ..utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/lock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def lock_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role.level >= user.role.level:
        abort(403)
    user.lock()
    flash('用户被锁定', 'info')
    return redirect_back()


@admin_bp.route('/unlock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unlock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unlock()
    flash('用户已解锁', 'info')
    return redirect_back()


@admin_bp.route('/block/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role.level >= user.role.level:
        abort(403)
    user.block()
    flash('用户被封禁', 'info')
    return redirect_back()


@admin_bp.route('/unblock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def unblock_user(user_id):
    user = User.query.get_or_404(user_id)
    user.unblock()
    flash('用户被解封', 'info')
    return redirect_back()


@admin_bp.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        role = Role.query.get(form.role.data)
        if role.name == 'Locked':
            user.lock()
        if role.name != 'Administrator':
            user.role = role
        user.bio = form.bio.data
        user.website = form.website.data
        user.confirmed = form.confirmed.data
        user.active = form.active.data
        user.location = form.location.data
        user.username = form.username.data
        user.email = form.email.data
        db.session.commit()
        flash('个人资料更新完成', 'success')
        return redirect_back()
    form.name.data = user.name
    form.role.data = user.role.id
    form.bio.data = user.bio
    form.website.data = user.website
    form.location.data = user.location
    form.username.data = user.username
    form.email.data = user.email
    form.confirmed.data = user.confirmed
    form.active.data = user.active
    return render_template('admin/edit_profile.html', form=form, user=user)


@admin_bp.route('/delete/tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
@permission_required('MODERATE')
def delete_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()
    flash('标签删除成功', 'info')
    return redirect_back()


@admin_bp.route('/')
@login_required
@permission_required('MODERATE')
def index():
    user_count = User.query.count()
    locked_user_count = User.query.filter_by(locked=True).count()
    blocked_user_count = User.query.filter_by(active=False).count()
    photo_count = Photo.query.count()
    reported_photos_count = Photo.query.filter(Photo.flag > 0).count()
    tag_count = Tag.query.count()
    comment_count = Comment.query.count()
    reported_comments_count = Comment.query.filter(Comment.flag > 0).count()
    return render_template('admin/index.html', user_count=user_count, photo_count=photo_count,
                           tag_count=tag_count, comment_count=comment_count, locked_user_count=locked_user_count,
                           blocked_user_count=blocked_user_count, reported_comments_count=reported_comments_count,
                           reported_photos_count=reported_photos_count)


@admin_bp.route('/manage/photo', defaults={'order': 'by_flag'})
@admin_bp.route('/manage/photo/<order>')
@login_required
@permission_required('MODERATE')
def manage_photo(order):
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_MANAGE_PHOTO_PER_PAGE']
    pagination = Photo.query
    order_rule = '举报数量'
    if order == 'by_flag':
        pagination = pagination.order_by(Photo.flag.desc())
    else:
        order_rule = '上传时间'
        pagination = pagination.order_by(Photo.timestamp.desc())
    pagination = pagination.paginate(page, per_page)
    photos = pagination.items
    return render_template('admin/manage_photo.html', pagination=pagination, photos=photos, order_rule=order_rule)


@admin_bp.route('/manage/user')
@login_required
@permission_required('MODERATE')
def manage_user():
    filter_rule = request.args.get('filter', 'all')  # 'all', 'locked', 'blocked', 'administrator', 'moderator'
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_MANAGE_USER_PER_PAGE']
    administrator = Role.query.filter_by(name='Administrator').first()
    moderator = Role.query.filter_by(name='Moderator').first()
    pagination = User.query
    if filter_rule == 'locked':
        pagination = pagination.filter_by(locked=True)
    elif filter_rule == 'blocked':
        pagination = pagination.filter_by(active=False)
    elif filter_rule == 'administrator':
        pagination = pagination.filter_by(role=administrator)
    elif filter_rule == 'moderator':
        pagination = pagination.filter_by(role=moderator)
    pagination = pagination.order_by(User.member_since.desc()).paginate(page, per_page)
    users = pagination.items
    return render_template('admin/manage_user.html', users=users, pagination=pagination)


@admin_bp.route('/manage/tag')
@login_required
@permission_required('MODERATE')
def manage_tag():
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_MANAGE_TAG_PER_PAGE']
    pagination = Tag.query.order_by(Tag.id.desc()).paginate(page, per_page)
    tags = pagination.items
    return render_template('admin/manage_tag.html', tags=tags, pagination=pagination)


@admin_bp.route('manage/comment', defaults={'order': 'by_flag'})
@admin_bp.route('manage/comment/<order>')
@login_required
@permission_required('MODERATE')
def manage_comment(order):
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_MANAGE_COMMENT_PER_PAGE']
    order_rule = '举报数量'
    pagination = Comment.query
    if order == 'by_time':
        order_rule = '评论时间'
        pagination = pagination.order_by(Comment.timestamp.desc())
    else:
        pagination = pagination.order_by(Comment.flag.desc())
    pagination = pagination.paginate(page, per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination, order_rule=order_rule)
