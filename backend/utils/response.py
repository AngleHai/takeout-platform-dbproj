from flask import jsonify


def success_response(data=None, message="成功", code=20000):
    """成功响应"""
    return jsonify({
        'code': code,
        'msg': message,
        'data': data
    })


def fail_response(data=None, message="失败", code=50000):
    """失败响应"""
    return jsonify({
        'code': code,
        'msg': message,
        'data': data
    })
