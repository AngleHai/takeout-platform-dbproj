import jwt
import datetime
from flask import request, current_app
from functools import wraps
from utils.response import fail_response


def token_required(f):
    """JWT 认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]

        if not token:
            return fail_response(None, 'Token缺失或格式不正确', 40100), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            request.user = data
        except jwt.ExpiredSignatureError:
            return fail_response(None, 'Token已过期', 40101), 401
        except jwt.InvalidTokenError:
            return fail_response(None, '无效的Token', 40102), 401

        return f(*args, **kwargs)
    return decorated


def role_required(*roles):
    """角色权限装饰器，需配合 @token_required 使用"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user_role = request.user.get('role')
            if user_role not in roles:
                return fail_response(None, '无权限访问', 40300), 403
            return f(*args, **kwargs)
        return decorated
    return decorator
