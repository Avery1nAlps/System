from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
import socket


# -------------------------- 基础角色权限装饰器 --------------------------
def has_role(role_codes):
    """通用角色校验装饰器"""

    def check_role(user):
        if not user.is_active:
            return False
        if not hasattr(user, 'profile'):
            return False
        if user.profile.status != 'ACTIVE':
            return False
        return user.profile.role.role_code in role_codes

    return user_passes_test(check_role, login_url='/login/')


# -------------------------- 快捷装饰器 --------------------------
is_admin = has_role(['ADMIN'])
is_general_accountant = has_role(['GENERAL_ACCOUNTANT', 'ADMIN'])
is_purchase_accountant = has_role(['PURCHASE_ACCOUNTANT', 'ADMIN'])
is_sales_accountant = has_role(['SALES_ACCOUNTANT', 'ADMIN'])
is_cashier = has_role(['CASHIER', 'ADMIN'])
is_accountant_supervisor = has_role(['ACCOUNTANT_SUPERVISOR', 'ADMIN'])
is_employee = has_role(['EMPLOYEE', 'ADMIN'])
is_hr_staff = has_role(['HR_STAFF', 'ADMIN'])


# -------------------------- 权限中间件 --------------------------
class RolePermissionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path in ['/login/', '/logout/'] or request.path.startswith('/static/') or request.path.startswith(
                '/admin/'):
            return None

        url_role_map = {
            '/finance/voucher/': ['GENERAL_ACCOUNTANT', 'ADMIN'],
            '/finance/posting/': ['GENERAL_ACCOUNTANT', 'ADMIN'],
            '/finance/reconciliation/': ['GENERAL_ACCOUNTANT', 'CASHIER', 'ADMIN'],
            '/finance/tax/': ['GENERAL_ACCOUNTANT', 'ADMIN'],
            '/finance/currency/': ['GENERAL_ACCOUNTANT', 'ADMIN'],
            '/finance/report/': ['GENERAL_ACCOUNTANT', 'ACCOUNTANT_SUPERVISOR', 'ADMIN'],
            '/finance/yearly_close/': ['ACCOUNTANT_SUPERVISOR', 'ADMIN'],
            '/finance/supplier/': ['PURCHASE_ACCOUNTANT', 'ADMIN'],
            '/finance/purchase_order/': ['PURCHASE_ACCOUNTANT', 'ADMIN'],
            '/finance/customer/': ['SALES_ACCOUNTANT', 'ADMIN'],
            '/finance/sales_order/': ['SALES_ACCOUNTANT', 'ADMIN'],
            '/employee/expense/': ['EMPLOYEE', 'ADMIN'],
            '/hr/employee_info/': ['HR_STAFF', 'ADMIN'],
        }

        for url_prefix, allowed_roles in url_role_map.items():
            if request.path.startswith(url_prefix):
                if not request.user.is_authenticated:
                    from django.shortcuts import redirect
                    return redirect('/login/')
                if not has_role(allowed_roles)(request.user):
                    raise PermissionDenied("你没有访问该功能的权限，请联系管理员")
        return None


# -------------------------- 辅助工具 --------------------------
def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def record_operation_log(request, operate_type, operate_module, operate_content):
    """记录用户操作日志（这里修改为users_app）"""
    from users_app.models import UserOperationLog  # 关键：改为users_app
    if request.user.is_authenticated:
        UserOperationLog.objects.create(
            user=request.user,
            operate_type=operate_type,
            operate_module=operate_module,
            operate_content=operate_content,
            ip_address=get_client_ip(request)
        )