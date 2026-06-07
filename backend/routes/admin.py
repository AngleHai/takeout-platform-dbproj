from flask import Blueprint, request, current_app
from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required, role_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/users', methods=['GET'])
@token_required
@role_required('管理员')
def get_all_users():
    """管理员获取所有用户列表"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        offset = (page - 1) * page_size
        keyword = request.args.get('keyword', '')
        role_filter = request.args.get('role', '')

        conditions = []
        params = []

        if keyword:
            conditions.append("(u.UserName LIKE %s OR u.UserID LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        if role_filter:
            conditions.append("u.Role = %s")
            params.append(role_filter)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # 总数
        count_query = f"SELECT COUNT(*) FROM user u {where_clause}"
        total = execute_query(conn, count_query, params, fetch_one=True)[0]

        # 分页查询
        query = f"""
            SELECT u.UserID, u.UserName, u.Password, u.Phone, u.Role
            FROM user u
            {where_clause}
            ORDER BY u.UserID
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        rows = execute_query(conn, query, params, fetch_all=True)

        users = [{
            'userId': r[0].strip(),
            'userName': r[1].strip(),
            'password': r[2],
            'phone': r[3].strip() if r[3] else None,
            'role': r[4].strip(),
        } for r in rows]

        return success_response({'list': users, 'total': total})
    except Exception as e:
        current_app.logger.error(f"获取用户列表错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@admin_bp.route('/admin/delete-user', methods=['POST'])
@token_required
@role_required('管理员')
def delete_user():
    """管理员删除用户"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        user_id = data.get('userId')
        admin_id = request.user.get('UserID')

        if not user_id:
            return fail_response(None, '用户ID不能为空', 40000)

        if user_id == admin_id:
            return fail_response(None, '不能删除自己', 40000)

        # 查询用户角色
        check_query = "SELECT Role FROM user WHERE UserID = %s"
        user_row = execute_query(conn, check_query, (user_id,), fetch_one=True)
        if not user_row:
            return fail_response(None, '用户不存在', 40400)

        role = user_row[0].strip()

        # 检查是否有未完成订单
        if role == '顾客':
            order_check = "SELECT OrderID FROM orders WHERE CustomerID = %s AND DeliveryStatus IN ('已接单', '配送中')"
        elif role == '商家':
            order_check = "SELECT OrderID FROM orders WHERE MerchantID = %s AND DeliveryStatus IN ('已接单', '配送中')"
        elif role == '送餐员':
            order_check = "SELECT l.OrderID FROM logistics l JOIN orders o ON l.OrderID = o.OrderID WHERE l.DeliverymanID = %s AND o.DeliveryStatus = '配送中'"
        else:
            order_check = None

        if order_check:
            active = execute_query(conn, order_check, (user_id,), fetch_all=True)
            if active:
                return fail_response(None, '该用户有未完成的订单，无法删除', 40000)

        # 删除子表记录
        if role == '顾客':
            execute_query(conn, "DELETE FROM address WHERE CustomerID = %s", (user_id,))
            execute_query(conn, "DELETE FROM customer WHERE UserID = %s", (user_id,))
        elif role == '商家':
            execute_query(conn, "DELETE FROM merchant WHERE UserID = %s", (user_id,))
        elif role == '送餐员':
            execute_query(conn, "DELETE FROM deliveryman WHERE UserID = %s", (user_id,))

        # 删除 user 表
        execute_query(conn, "DELETE FROM user WHERE UserID = %s", (user_id,))

        return success_response(None, '删除成功')
    except Exception as e:
        current_app.logger.error(f"删除用户错误: {e}")
        return fail_response(None, f'删除失败: {str(e)}', 50000)
