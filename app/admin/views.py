from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
def dashboard():
    return 'dashboard'


# @admin_bp.route('/category/add')
# def add_category()