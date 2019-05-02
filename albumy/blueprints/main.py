from flask import Blueprint, render_template, request, current_app, send_from_directory, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from ..decorators import confirm_required, permission_required
from ..extensions import db
from ..forms.main import DescriptionForm, TagForm, CommentForm
from ..models import Photo, Tag, Comment, Collect, Notification
from ..notifications import push_collect_notification, push_commit_notification
from ..utils import flash_errors, redirect_back, validate_image

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('main/index.html')


@main_bp.route('/explore')
def explore():
    return render_template('main/explore.html')


@main_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@confirm_required
@permission_required('UPLOAD')
def upload():
    if request.method == 'POST' and 'file' in request.files:
        f = request.files.get('file')
        result = validate_image(f)
        if result is None:
            return '不支持的图片格式', 400
        photo = Photo(
            filename=result['name'],
            filename_m=result['name_m'],
            filename_s=result['name_s'],
            author=current_user._get_current_object()
        )
        db.session.add(photo)
        db.session.commit()
    return render_template('main/upload.html')


@main_bp.route('/avatars/<path:filename>')
def get_avatar(filename):
    return send_from_directory(current_app.config['AVATARS_SAVE_PATH'], filename)


@main_bp.route('/uploads/<path:filename>')
def get_image(filename):
    return send_from_directory(current_app.config['ALBUMY_UPLOAD_PATH'], filename)


@main_bp.route('/photo/<int:photo_id>')
def show_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_COMMENT_PER_PAGE']
    pagination = Comment.query.with_parent(photo).order_by(Comment.timestamp.desc()).paginate(page, per_page)
    comments = pagination.items

    description_form = DescriptionForm()
    tag_form = TagForm()
    comment_form = CommentForm()

    description_form.description.data = photo.description

    return render_template('main/photo.html', photo=photo, description_form=description_form, tag_form=tag_form,
                           pagination=pagination, comments=comments, comment_form=comment_form)


@main_bp.route('/photo/n/<int:photo_id>')
def photo_next(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_n = Photo.query.with_parent(photo.author).filter(Photo.id < photo_id).order_by(Photo.id.desc()).first()

    if photo_n is None:
        flash('已经是最后一个了', 'info')
        return redirect(url_for('.show_photo', photo_id=photo_id))
    return redirect(url_for('.show_photo', photo_id=photo_n.id))


@main_bp.route('/photo/p/<int:photo_id>')
def photo_prev(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo_p = Photo.query.with_parent(photo.author).filter(Photo.id > photo_id).order_by(Photo.id.asc()).first()

    if photo_p is None:
        flash('已经是第一个了', 'info')
        return redirect(url_for('.show_photo', photo_id=photo.id))
    return redirect(url_for('.show_photo', photo_id=photo_p.id))


@main_bp.route('/delete/photo/<int:photo_id>', methods=['POST'])
@login_required
def delete_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    db.session.delete(photo)
    db.session.commit()

    photo_n = Photo.query.with_parent(photo.author).filter(Photo.id < photo_id).order_by(Photo.id.desc()).first()
    if photo_n is None:
        photo_p = Photo.query.with_parent(photo.author).filter(Photo.id > photo_id).order_by(Photo.id.asc()).first()
        if photo_p is None:
            return redirect(url_for('user.index', username=photo.author.username))
        return redirect(url_for('.show_photo', photo_id=photo_p.id))
    return redirect(url_for('.show_photo', photo_id=photo_n.id))


@main_bp.route('/report/photo/<int:photo_id>', methods=['POST'])
@login_required
@confirm_required
def report_photo(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    photo.flag += 1
    db.session.commit()
    flash('操作成功', 'success')
    return redirect(url_for('.show_photo', photo_id=photo_id))


@main_bp.route('/photo/<int:photo_id>/description', methods=['POST'])
@login_required
def edit_description(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    form = DescriptionForm()
    if form.validate_on_submit():
        photo.description = form.description.data
        db.session.commit()
        flash('描述修改成功', 'success')
        return redirect(url_for('.show_photo', photo_id=photo_id))
    flash_errors(form)
    return redirect(url_for('.show_photo', photo_id=photo_id))


@main_bp.route('/photo/<int:photo_id>/tag', methods=['POST'])
@login_required
def new_tag(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)
    form = TagForm()
    if form.validate_on_submit():
        for tag_name in form.tag.data.split():
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag is None:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
            if tag not in photo.tags:
                photo.tags.append(tag)
                db.session.commit()
        flash('标签已添加', 'success')
        return redirect(url_for('.show_photo', photo_id=photo_id))
    flash_errors(form)
    return redirect(url_for('.show_photo', photo_id=photo.id))


@main_bp.route('/delete/tag/<int:photo_id>/<int:tag_id>', methods=['POST'])
@login_required
def delete_tag(photo_id, tag_id):
    tag = Tag.query.get_or_404(tag_id)
    photo = Photo.query.get_or_404(photo_id)
    if current_user != photo.author:
        abort(403)

    photo.tags.remove(tag)
    db.session.commit()

    if not tag.photos:
        db.session.delete(tag)
        db.session.commit()

    flash('标签已删除', 'info')
    return redirect(url_for('.show_photo', photo_id=photo.id))


@main_bp.route('/tag/<int:tag_id>', defaults={'order': 'by_time'})
@main_bp.route('/tag/<int:tag_id>/<any(by_time, by_collects):order>')
def show_tag(tag_id, order):
    tag = Tag.query.get_or_404(tag_id)
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_PHOTO_PER_PAGE']
    order_rule = '时间'
    pagination = Photo.query.with_parent(tag).order_by(Photo.timestamp.desc()).paginate(page, per_page)
    photos = pagination.items

    if order == 'by_collects':
        order_rule = '收藏量'
        photos.sort(lambda x: len(x.collectors), reverse=True)
    return render_template('main/tag.html', tag=tag, pagination=pagination, photos=photos, order_rule=order_rule)


@main_bp.route('/set-comment/<int:photo_id>')
@login_required
def set_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get('page', 1, type=int)
    if current_user != photo.author:
        abort(403)
    if photo.can_comment:
        photo.can_comment = False
        flash('评论已关闭', 'info')
    else:
        photo.can_comment = True
        flash('评论已开启', 'info')
    db.session.commit()
    return redirect(url_for('.show_photo', photo_id=photo_id, page=page))


@main_bp.route('/photo/<int:photo_id>/comment/new', methods=['POST'])
@login_required
@permission_required('COMMENT')
def new_comment(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get('page', 1, type=int)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data)
        comment.author = current_user._get_current_object()
        comment.photo = photo

        replied_id = request.args.get('reply')
        if replied_id:
            comment.replied = Comment.query.get_or_404(replied_id)
        db.session.add(comment)
        db.session.commit()
        if photo.author.receive_comment_notification:
            push_commit_notification(photo_id, photo.author, page=1)
        flash('已评论', 'success')
        return redirect(url_for('.show_photo', photo_id=photo_id, page=1))
    flash_errors(form)
    return redirect(url_for('.show_photo', photo_id=photo_id, page=page))


@main_bp.route('/reply/comment/<int:comment_id>')
@login_required
@permission_required('COMMENT')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    return redirect(url_for('.show_photo', photo_id=comment.photo.id, reply=comment_id,
                            author=comment.author.name) + '#comment-form')


@main_bp.route('/delete/comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if current_user != comment.author and current_user != comment.photo.author:
        abort(403)
    db.session.delete(comment)
    db.session.commit()
    flash('删除成功', 'info')
    return redirect_back()


@main_bp.route('/report/comment/<int:comment_id>')
@login_required
@confirm_required
def report_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.flag += 1
    db.session.commit()
    flash('已举报', 'success')
    return redirect(url_for('.show_photo', photo_id=comment.photo_id))


@main_bp.route('/collect/<int:photo_id>', methods=['POST'])
@login_required
@confirm_required
@permission_required('COLLECT')
def collect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if current_user.is_collecting(photo):
        flash('当前图片已经收藏', 'info')
        return redirect(url_for('.show_photo', photo_id=photo_id))
    current_user.collect(photo)
    if photo.author.receive_collect_notification:
        push_collect_notification(current_user, photo_id, photo.author)
    flash('收藏成功!', 'success')
    return redirect(url_for('.show_photo', photo_id=photo_id))


@main_bp.route('/uncollect/<int:photo_id>', methods=['POST'])
@login_required
def uncollect(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    if not current_user.is_collecting(photo):
        flash('错误的操作, 图片没有收藏', 'info')
        return redirect(url_for('.show_photo', photo_id=photo_id))
    current_user.uncollect(photo)
    flash('已取消收藏', 'success')
    return redirect(url_for('.show_photo', photo_id=photo_id))


@main_bp.route('/photo/<int:photo_id>/collectors')
def show_collectors(photo_id):
    photo = Photo.query.get_or_404(photo_id)
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ALBUMY_USER_PER_PAGE']
    pagination = Collect.query.with_parent(photo).order_by(Collect.timestamp.asc()).paginate(page, per_page)
    collects = pagination.items
    return render_template('main/collectors.html', collects=collects, photo=photo, pagination=pagination)


@main_bp.route('/notifications')
@login_required
def show_notifications():
    page = request.args.get('page', 1, int)
    per_page = current_app.config['ALBUMY_NOTIFICATION_PER_PAGE']
    notifications = Notification.query.with_parent(current_user)
    filter_rule = request.args.get('filter')
    if filter_rule == 'unread':
        notifications = notifications.filter_by(is_read=False)
    pagination = notifications.order_by(Notification.timestamp.desc()).paginate(page, per_page)
    notifications = pagination.items
    return render_template('main/notifications.html', pagination=pagination, notifications=notifications)


@main_bp.route('/notifications/read/<int:notification_id>', methods=['POST'])
@login_required
def read_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if current_user != notification.receiver:
        abort(403)

    notification.is_read = True
    db.session.commit()
    flash('消息已读', 'success')
    return redirect_back()


@main_bp.route('/notifications/read/all', methods=['POST'])
@login_required
def read_all_notification():
    notifications = Notification.query.with_parent(current_user).all()
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    flash('全部消息已读', 'success')
    return redirect_back()
