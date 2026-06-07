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
