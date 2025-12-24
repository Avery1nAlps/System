# users_app/templatetags/permission_tags.py
from django import template

register = template.Library()


@register.filter
def has_permission(user, permission_type):
    """
    模板标签：检查用户是否有特定权限
    permission_type: 'voucher', 'supplier', 'customer'
    """
    if not user.is_authenticated:
        return False

    # admin用户有所有权限
    if user.username == 'admin':
        return True

    # 检查用户是否有profile和角色
    if not hasattr(user, 'profile'):
        return False

    role_code = user.profile.role.role_code

    # 定义角色权限
    role_permissions = {
        'ADMIN': ['voucher', 'supplier', 'customer'],
        'GENERAL_ACCOUNTANT': ['voucher'],
        'PURCHASE_ACCOUNTANT': ['voucher', 'supplier'],
        'SALES_ACCOUNTANT': ['voucher', 'customer'],
        'ACCOUNTANT_SUPERVISOR': ['voucher', 'supplier', 'customer'],
        'CASHIER': ['voucher'],
        'EMPLOYEE': [],
        'HR_STAFF': [],
    }

    # 检查权限
    if role_code in role_permissions:
        return permission_type in role_permissions[role_code]

    return False