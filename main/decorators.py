# main/decorators.py
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from functools import wraps
from .models import Role


def role_required(*allowed_roles):
    """
    Decorator kiểm tra role của user
    Usage:
        @role_required(Role.USER, Role.ADMIN)
        def some_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied(
                    "Bạn không có quyền truy cập chức năng này.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def user_required(view_func):
    """Chỉ User (không phải Admin, Guest)"""
    return role_required(Role.USER)(view_func)


def admin_required(view_func):
    """Chỉ Admin"""
    return role_required(Role.ADMIN)(view_func)


def user_or_admin_required(view_func):
    """User hoặc Admin (đã đăng nhập)"""
    return role_required(Role.USER, Role.ADMIN)(view_func)
