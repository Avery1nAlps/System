from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps


def accounting_permission_required(permission_type):
    """
    会计权限装饰器
    permission_type: 'voucher', 'supplier', 'customer'
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            from .utils import check_accounting_permission  # 从utils导入

            if check_accounting_permission(request.user, permission_type):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, '您没有访问此页面的权限')
                return redirect('users:home')

        return _wrapped_view

    return decorator


def admin_required(view_func):
    """管理员权限装饰器"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.username == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, '此功能仅限管理员访问')
            return redirect('users:home')

    return _wrapped_view