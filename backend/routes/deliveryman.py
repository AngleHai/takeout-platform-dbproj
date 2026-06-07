from flask import Blueprint, current_app
from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required, role_required

deliveryman_bp = Blueprint('deliveryman', __name__)


@deliveryman_bp.route('/deliveryman/available', methods=['GET'])
@token_required
@role_required('商家')
def get_available_deliverymen():
    """获取空闲送餐员列表"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        query = """
            SELECT d.UserID, u.UserName, d.WorkStatus, u.Phone
            FROM deliveryman d
            JOIN user u ON d.UserID = u.UserID
            WHERE d.WorkStatus = '空闲'
        """
        rows = execute_query(conn, query, fetch_all=True)
        result = [{
            'userId': r[0],
            'name': r[1],
            'workStatus': r[2],
            'phone': r[3]
        } for r in rows]

        return success_response(result)
    except Exception as e:
        current_app.logger.error(f"获取送餐员列表错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)
