from flask import Blueprint, flash, abort
from flask_login import login_required, current_user

from ..decorators import permission_required
from ..models import User
from ..utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/lock/user/<int:user_id>', methods=['POST'])
@login_required
@permission_required('MODERATE')
def lock_user(user_id):
    user = User.query.get_or_404(user_id)
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


@admin_bp.route('/block/user/<int:user_id>')
@login_required
@permission_required('MODERATE')
def block_user(user_id):
    user = User.query.get_or_404(user_id)
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


@admin_bp.route('/<int:user_id>')
def edit_profile_admin(user_id):
    pass


@admin_bp.route('/<int:tag_id>')
def delete_tag(tag_id):
    pass
