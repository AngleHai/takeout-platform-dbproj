import datetime
from flask import Blueprint, request, current_app
import jwt

from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/user/login', methods=['POST'])
def login():
    """用户登录"""
    if not request.is_json:
        return fail_response(None, '请求必须是JSON格式', 40000)

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return fail_response(None, '用户名或密码不能为空', 40000)

    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        query = "SELECT UserID, UserName, Password, Role FROM user WHERE UserName = %s"
        user_record = execute_query(conn, query, (username,), fetch_one=True)

        if user_record:
            user_id, db_username, db_password, role = user_record
            user_id = user_id.strip()
            db_username = db_username.strip()
            role = role.strip()
            if password == db_password:
                payload = {
                    'UserID': user_id,
                    'username': db_username,
                    'role': role,
                    'exp': datetime.datetime.now(datetime.timezone.utc) + current_app.config['JWT_ACCESS_TOKEN_EXPIRES']
                }
                token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm="HS256")
                return success_response({
                    'token': token,
                    'userInfo': {
                        'name': db_username,
                        'role': role,
                        'userId': user_id
                    }
                }, '登录成功')
            else:
                return fail_response(None, '用户名或密码错误', 40100)
        else:
            return fail_response(None, '用户不存在', 40100)
    except Exception as e:
        current_app.logger.error(f"登录错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@auth_bp.route('/user/register', methods=['POST'])
def register():
    """用户注册"""
    if not request.is_json:
        return fail_response(None, '请求必须是JSON格式', 40000)

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    phone = data.get('phone')
    role = data.get('role')

    if not all([username, password, role]):
        return fail_response(None, '用户名、密码、角色不能为空', 40000)

    if len(password) < 6:
        return fail_response(None, '密码至少6位', 40000)

    if role not in ('顾客', '商家', '配送员'):
        return fail_response(None, '角色必须是顾客/商家/配送员', 40000)

    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        # 检查用户名是否已存在
        check_query = "SELECT UserID FROM user WHERE UserName = %s"
        existing = execute_query(conn, check_query, (username,), fetch_one=True)
        if existing:
            return fail_response(None, '用户名已存在', 40000)

        # 生成新 UserID
        id_query = "SELECT MAX(UserID) FROM user"
        max_id = execute_query(conn, id_query, fetch_one=True)
        if max_id and max_id[0]:
            new_num = int(max_id[0][1:]) + 1
        else:
            new_num = 1
        new_user_id = f"U{new_num:07d}"

        # 插入 user 表
        insert_user = "INSERT INTO user (UserID, UserName, Password, Phone, Role) VALUES (%s, %s, %s, %s, %s)"
        execute_query(conn, insert_user, (new_user_id, username, password, phone, role))

        # 根据角色插入子表
        if role == '顾客':
            name = data.get('name', username)
            gender = data.get('gender')
            age = data.get('age')
            email = data.get('email')
            insert_sub = "INSERT INTO customer (UserID, Name, Gender, Age, Email) VALUES (%s, %s, %s, %s, %s)"
            execute_query(conn, insert_sub, (new_user_id, name, gender, age, email))
        elif role == '商家':
            shop_name = data.get('shopName', username)
            insert_sub = "INSERT INTO merchant (UserID, ShopName) VALUES (%s, %s)"
            execute_query(conn, insert_sub, (new_user_id, shop_name))
        elif role == '配送员':
            insert_sub = "INSERT INTO deliveryman (UserID, WorkStatus) VALUES (%s, %s)"
            execute_query(conn, insert_sub, (new_user_id, '空闲'))

        return success_response({'userId': new_user_id}, '注册成功')
    except Exception as e:
        current_app.logger.error(f"注册错误: {e}")
        return fail_response(None, f'注册失败: {str(e)}', 50000)


@auth_bp.route('/user/info', methods=['POST'])
@token_required
def get_user_info():
    """获取当前用户信息"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        user_id = request.user.get('UserID')
        role = request.user.get('role')

        # 基础信息
        base_query = "SELECT UserID, UserName, Phone, Role FROM user WHERE UserID = %s"
        base_info = execute_query(conn, base_query, (user_id,), fetch_one=True)

        if not base_info:
            return fail_response(None, '用户不存在', 40400)

        user_info = {
            'userId': base_info[0].strip(),
            'name': base_info[1].strip(),
            'phone': base_info[2].strip() if base_info[2] else None,
            'role': base_info[3].strip()
        }

        # 子表补充信息
        if role == '顾客':
            sub_query = "SELECT Name, Gender, Age, Email FROM customer WHERE UserID = %s"
            sub_info = execute_query(conn, sub_query, (user_id,), fetch_one=True)
            if sub_info:
                user_info.update({'realName': sub_info[0], 'gender': sub_info[1], 'age': sub_info[2], 'email': sub_info[3]})
        elif role == '商家':
            sub_query = "SELECT ShopName FROM merchant WHERE UserID = %s"
            sub_info = execute_query(conn, sub_query, (user_id,), fetch_one=True)
            if sub_info:
                user_info['shopName'] = sub_info[0]
        elif role == '配送员':
            sub_query = "SELECT WorkStatus FROM deliveryman WHERE UserID = %s"
            sub_info = execute_query(conn, sub_query, (user_id,), fetch_one=True)
            if sub_info:
                user_info['workStatus'] = sub_info[0]

        return success_response(user_info)
    except Exception as e:
        current_app.logger.error(f"获取用户信息错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@auth_bp.route('/user/logout', methods=['POST'])
@token_required
def logout():
    """用户登出"""
    return success_response(None, '登出成功')
