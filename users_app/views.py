from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# 临时首页（仅登录用户可访问，添加@login_required装饰器做权限校验）
@login_required(login_url='users:login')  # 未登录用户自动跳转到登录页
def home(request):
    # 传递用户信息到模板（用户名、角色、部门等）
    context = {
        'username': request.user.username,
        'role': request.user.profile.role.get_role_name_display(),  # 显示角色友好名称（如“系统管理员”）
        'department': request.user.profile.department,
        'employee_id': request.user.profile.employee_id,
    }
    return render(request, 'users/home.html', context)


def check_accounting_permission(user, required_permission):
    """
    检查用户是否有会计相关权限
    required_permission: 'voucher', 'supplier', 'customer', 'all'
    """
    if not user.is_authenticated:
        return False

    # admin用户有所有权限
    if user.username == 'admin':
        return True

    # 获取用户角色
    if hasattr(user, 'profile'):
        role_code = user.profile.role.role_code

        # 定义权限映射
        role_permissions = {
            'ADMIN': ['voucher', 'supplier', 'customer', 'all'],  # 管理员有所有权限
            'GENERAL_ACCOUNTANT': ['voucher'],  # 总账会计只有凭证权限
            'PURCHASE_ACCOUNTANT': ['voucher', 'supplier'],  # 采购会计有凭证和供应商权限
            'SALES_ACCOUNTANT': ['voucher', 'customer'],  # 销售会计有凭证和客户权限
            'ACCOUNTANT_SUPERVISOR': ['voucher', 'supplier', 'customer'],  # 会计主管有所有会计权限
            'CASHIER': ['voucher'],  # 出纳只有凭证权限
        }

        # 检查权限
        if role_code in role_permissions:
            if required_permission == 'all':
                return True
            return required_permission in role_permissions[role_code]

    return False