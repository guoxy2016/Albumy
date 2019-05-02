from flask import Blueprint, render_template, jsonify
from flask_login import current_user

from ..models import User, Notification
from ..notifications import push_follow_notification

ajax_bp = Blueprint('ajax', __name__, )


@ajax_bp.route('/profile/<int:user_id>')
def get_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('main/profile_popup.html', user=user)


@ajax_bp.route('/follow/<username>', methods=['POST'])
def follow(username):
    if not current_user.is_authenticated:
        return jsonify(message='用户未登录'), 403
    if not current_user.confirmed:
        return jsonify(message='请验证邮箱后操作'), 400
    if not current_user.can('FOLLOW'):
        return jsonify(message='没有权限'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if current_user.is_following(user):
        return jsonify(message='重复的操作, 以关注用户'), 400

    current_user.follow(user)
    if user.receive_follow_notification:
        push_follow_notification(current_user, user)
    return jsonify(message='已关注用户')


@ajax_bp.route('/unfollow/<username>', methods=['POST'])
def unfollow(username):
    if not current_user.is_authenticated:
        return jsonify(message='用户未登录'), 403

    user = User.query.filter_by(username=username).first_or_404()
    if not current_user.is_following(user):
        return jsonify(message='无效的操作, 您为关注该用户'), 400

    current_user.unfollow(user)
    return jsonify(message='已取消关注')


@ajax_bp.route('/followers-count/<int:user_id>')
def followers_count(user_id):
    user = User.query.get_or_404(user_id)
    count = user.followers.count() - 1
    return jsonify(count=count)


@ajax_bp.route('/notifications-count')
def notifications_count():
    if not current_user.is_authenticated:
        return jsonify(message='用户未登录'), 403
    count = Notification.query.with_parent(current_user).filter_by(is_read=False).count()
    return jsonify(count=count)


@ajax_bp.errorhandler(400)
def bad_require(e):
    return jsonify(message=e.description), 400


@ajax_bp.errorhandler(404)
def not_found(e):
    return jsonify(message=e.description), 404


@ajax_bp.errorhandler(500)
def server_error(e):
    return jsonify(message=e.description), 500
