from flask import Blueprint, request, current_app
from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required, role_required

address_bp = Blueprint('address', __name__)


@address_bp.route('/address/list', methods=['GET'])
@token_required
@role_required('顾客')
def get_address_list():
    """获取当前顾客的地址列表"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        customer_id = request.user.get('UserID')
        query = """
            SELECT AddressID, ReceiverName, ReceiverPhone, DetailAddress, IsDefault
            FROM address
            WHERE CustomerID = %s
            ORDER BY IsDefault DESC
        """
        rows = execute_query(conn, query, (customer_id,), fetch_all=True)
        addresses = [{
            'addressId': r[0],
            'receiverName': r[1],
            'receiverPhone': r[2],
            'detailAddress': r[3],
            'isDefault': bool(r[4])
        } for r in rows]

        return success_response(addresses)
    except Exception as e:
        current_app.logger.error(f"获取地址列表错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@address_bp.route('/address/add', methods=['POST'])
@token_required
@role_required('顾客')
def add_address():
    """添加收货地址"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        customer_id = request.user.get('UserID')
        receiver_name = data.get('receiverName')
        receiver_phone = data.get('receiverPhone')
        detail_address = data.get('detailAddress')
        is_default = data.get('isDefault', False)

        if not all([receiver_name, receiver_phone, detail_address]):
            return fail_response(None, '收货人、电话、地址不能为空', 40000)

        import re
        if not re.match(r'^1\d{10}$', receiver_phone):
            return fail_response(None, '联系电话格式不正确，需为11位手机号', 40000)

        # 生成地址ID
        id_query = "SELECT MAX(AddressID) FROM address"
        max_id = execute_query(conn, id_query, fetch_one=True)
        if max_id and max_id[0]:
            new_num = int(max_id[0][1:]) + 1
        else:
            new_num = 1
        new_addr_id = f"A{new_num:07d}"

        # 如果设为默认，先取消其他默认
        if is_default:
            execute_query(conn, "UPDATE address SET IsDefault = FALSE WHERE CustomerID = %s", (customer_id,))

        insert_query = """
            INSERT INTO address (AddressID, CustomerID, ReceiverName, ReceiverPhone, DetailAddress, IsDefault)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        execute_query(conn, insert_query, (new_addr_id, customer_id, receiver_name, receiver_phone, detail_address, is_default))

        return success_response({'addressId': new_addr_id}, '添加成功')
    except Exception as e:
        current_app.logger.error(f"添加地址错误: {e}")
        return fail_response(None, f'添加失败: {str(e)}', 50000)


@address_bp.route('/address/update', methods=['POST'])
@token_required
@role_required('顾客')
def update_address():
    """修改收货地址"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        customer_id = request.user.get('UserID')
        address_id = data.get('addressId')

        if not address_id:
            return fail_response(None, '地址ID不能为空', 40000)

        # 验证地址属于当前顾客
        check_query = "SELECT AddressID FROM address WHERE AddressID = %s AND CustomerID = %s"
        exists = execute_query(conn, check_query, (address_id, customer_id), fetch_one=True)
        if not exists:
            return fail_response(None, '地址不存在或无权修改', 40300)

        updates = []
        params = []
        for field, col in [('receiverName', 'ReceiverName'), ('receiverPhone', 'ReceiverPhone'), ('detailAddress', 'DetailAddress')]:
            if field in data:
                updates.append(f"{col} = %s")
                params.append(data[field])

        import re
        if 'receiverPhone' in data and not re.match(r'^1\d{10}$', data['receiverPhone']):
            return fail_response(None, '联系电话格式不正确，需为11位手机号', 40000)

        if 'isDefault' in data and data['isDefault']:
            execute_query(conn, "UPDATE address SET IsDefault = FALSE WHERE CustomerID = %s", (customer_id,))
            updates.append("IsDefault = %s")
            params.append(True)

        if not updates:
            return fail_response(None, '无更新内容', 40000)

        params.extend([address_id, customer_id])
        update_query = f"UPDATE address SET {', '.join(updates)} WHERE AddressID = %s AND CustomerID = %s"
        execute_query(conn, update_query, params)

        return success_response(None, '修改成功')
    except Exception as e:
        current_app.logger.error(f"修改地址错误: {e}")
        return fail_response(None, f'修改失败: {str(e)}', 50000)


@address_bp.route('/address/delete', methods=['POST'])
@token_required
@role_required('顾客')
def delete_address():
    """删除收货地址"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        customer_id = request.user.get('UserID')
        address_id = data.get('addressId')

        if not address_id:
            return fail_response(None, '地址ID不能为空', 40000)

        # 检查该地址是否被未完成订单使用
        order_check = """
            SELECT OrderID FROM orders
            WHERE AddressID = %s AND CustomerID = %s AND DeliveryStatus IN ('已接单', '配送中')
        """
        active = execute_query(conn, order_check, (address_id, customer_id), fetch_all=True)
        if active:
            return fail_response(None, '该地址有未完成订单，暂不能删除', 40000)

        delete_query = "DELETE FROM address WHERE AddressID = %s AND CustomerID = %s"
        execute_query(conn, delete_query, (address_id, customer_id))

        return success_response(None, '删除成功')
    except Exception as e:
        current_app.logger.error(f"删除地址错误: {e}")
        return fail_response(None, f'删除失败: {str(e)}', 50000)
