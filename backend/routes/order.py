from flask import Blueprint, request, current_app
from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required, role_required

order_bp = Blueprint('order', __name__)


@order_bp.route('/order/list', methods=['GET'])
@token_required
def get_order_list():
    """获取订单列表，根据角色返回不同数据"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        user_id = request.user.get('UserID')
        role = request.user.get('role')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        status = request.args.get('status')
        offset = (page - 1) * page_size

        conditions = []
        params = []

        # 根据角色过滤
        if role == '顾客':
            conditions.append("o.CustomerID = %s")
            params.append(user_id)
        elif role == '商家':
            conditions.append("o.MerchantID = %s")
            params.append(user_id)
        elif role == '配送员':
            conditions.append("l.DeliverymanID = %s")
            params.append(user_id)

        if status:
            conditions.append("o.DeliveryStatus = %s")
            params.append(status)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # 配送员需要 JOIN logistics
        join_clause = ""
        if role == '配送员':
            join_clause = "LEFT JOIN logistics l ON o.OrderID = l.OrderID"

        # 总数
        count_query = f"SELECT COUNT(*) FROM orders o {join_clause} {where_clause}"
        total = execute_query(conn, count_query, params, fetch_one=True)[0]

        # 分页查询
        query = f"""
            SELECT o.OrderID, o.CustomerID, o.MerchantID, o.OrderAmount,
                   o.PaymentMethod, o.OrderTime, o.DeliveryStatus,
                   c.Name AS CustomerName, m.ShopName
            FROM orders o
            JOIN customer c ON o.CustomerID = c.UserID
            JOIN merchant m ON o.MerchantID = m.UserID
            {join_clause}
            {where_clause}
            ORDER BY o.OrderTime DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        rows = execute_query(conn, query, params, fetch_all=True)

        orders = [{
            'orderId': r[0],
            'customerId': r[1],
            'merchantId': r[2],
            'orderAmount': float(r[3]),
            'paymentMethod': r[4],
            'orderTime': r[5].strftime('%Y-%m-%d %H:%M:%S') if r[5] else None,
            'deliveryStatus': r[6],
            'customerName': r[7],
            'shopName': r[8]
        } for r in rows]

        return success_response({'list': orders, 'total': total})
    except Exception as e:
        current_app.logger.error(f"获取订单列表错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@order_bp.route('/order/detail', methods=['GET'])
@token_required
def get_order_detail():
    """获取订单详情（含菜品列表）"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        order_id = request.args.get('orderId')
        if not order_id:
            return fail_response(None, '订单ID不能为空', 40000)

        # 订单基本信息
        query = """
            SELECT o.OrderID, o.CustomerID, o.MerchantID, o.AddressID,
                   o.OrderAmount, o.PaymentMethod, o.OrderTime, o.DeliveryStatus,
                   c.Name AS CustomerName, m.ShopName,
                   a.ReceiverName, a.ReceiverPhone, a.DetailAddress
            FROM orders o
            JOIN customer c ON o.CustomerID = c.UserID
            JOIN merchant m ON o.MerchantID = m.UserID
            JOIN address a  ON o.AddressID = a.AddressID AND o.CustomerID = a.CustomerID
            WHERE o.OrderID = %s
        """
        row = execute_query(conn, query, (order_id,), fetch_one=True)
        if not row:
            return fail_response(None, '订单不存在', 40400)

        order_info = {
            'orderId': row[0],
            'customerId': row[1],
            'merchantId': row[2],
            'addressId': row[3],
            'orderAmount': float(row[4]),
            'paymentMethod': row[5],
            'orderTime': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None,
            'deliveryStatus': row[7],
            'customerName': row[8],
            'shopName': row[9],
            'receiverName': row[10],
            'receiverPhone': row[11],
            'detailAddress': row[12]
        }

        # 菜品列表
        dish_query = """
            SELECT od.DishID, d.DishName, d.Price, od.Quantity
            FROM order_dish od
            JOIN dish d ON od.DishID = d.DishID
            WHERE od.OrderID = %s
        """
        dish_rows = execute_query(conn, dish_query, (order_id,), fetch_all=True)
        order_info['dishes'] = [{
            'dishId': d[0],
            'dishName': d[1],
            'price': float(d[2]),
            'quantity': d[3]
        } for d in dish_rows]

        # 配送信息
        logistics_query = """
            SELECT l.DeliverymanID, u.UserName, l.EstimatedTime, l.IsDelivered, l.CustomerPhone
            FROM logistics l
            JOIN user u ON l.DeliverymanID = u.UserID
            WHERE l.OrderID = %s
        """
        log_row = execute_query(conn, logistics_query, (order_id,), fetch_one=True)
        if log_row:
            order_info['logistics'] = {
                'deliverymanId': log_row[0],
                'deliverymanName': log_row[1],
                'estimatedTime': log_row[2].strftime('%Y-%m-%d %H:%M:%S') if log_row[2] else None,
                'isDelivered': bool(log_row[3]),
                'customerPhone': log_row[4]
            }

        return success_response(order_info)
    except Exception as e:
        current_app.logger.error(f"获取订单详情错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@order_bp.route('/order/create', methods=['POST'])
@token_required
@role_required('顾客')
def create_order():
    """顾客下单"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        customer_id = request.user.get('UserID')
        merchant_id = data.get('merchantId')
        address_id = data.get('addressId')
        payment_method = data.get('paymentMethod')
        dishes = data.get('dishes')  # [{dishId, quantity}, ...]

        if not all([merchant_id, address_id, dishes]):
            return fail_response(None, '商家、地址、菜品不能为空', 40000)

        if not isinstance(dishes, list) or len(dishes) == 0:
            return fail_response(None, '至少选择一个菜品', 40000)

        # 验证地址属于该顾客
        addr_check = "SELECT AddressID FROM address WHERE AddressID = %s AND CustomerID = %s"
        addr_exists = execute_query(conn, addr_check, (address_id, customer_id), fetch_one=True)
        if not addr_exists:
            return fail_response(None, '收货地址无效', 40000)

        # 计算总金额并验证菜品
        total_amount = 0
        for item in dishes:
            dish_query = "SELECT Price, MerchantID FROM dish WHERE DishID = %s"
            dish_info = execute_query(conn, dish_query, (item['dishId'],), fetch_one=True)
            if not dish_info:
                return fail_response(None, f"菜品 {item['dishId']} 不存在", 40000)
            if dish_info[1] != merchant_id:
                return fail_response(None, '所有菜品必须来自同一商家', 40000)
            total_amount += float(dish_info[0]) * item['quantity']

        # 生成订单ID（使用 SELECT ... FOR UPDATE 防止并发冲突）
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT MAX(OrderID) FROM orders FOR UPDATE")
            max_id = cursor.fetchone()
            if max_id and max_id[0]:
                new_num = int(max_id[0][1:]) + 1
            else:
                new_num = 1
            new_order_id = f"O{new_num:07d}"

            # 插入订单
            insert_order = """
                INSERT INTO orders (OrderID, CustomerID, MerchantID, AddressID, OrderAmount, PaymentMethod, OrderTime, DeliveryStatus)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), '已接单')
            """
            cursor.execute(insert_order, (new_order_id, customer_id, merchant_id, address_id, total_amount, payment_method))

            # 插入订单-菜品关联
            for item in dishes:
                insert_od = "INSERT INTO order_dish (OrderID, DishID, Quantity) VALUES (%s, %s, %s)"
                cursor.execute(insert_od, (new_order_id, item['dishId'], item['quantity']))

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

        return success_response({'orderId': new_order_id, 'orderAmount': total_amount}, '下单成功')
    except Exception as e:
        current_app.logger.error(f"创建订单错误: {e}")
        return fail_response(None, f'下单失败: {str(e)}', 50000)


@order_bp.route('/order/cancel', methods=['POST'])
@token_required
@role_required('顾客')
def cancel_order():
    """顾客取消订单（仅限未配送状态）"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        order_id = data.get('orderId')
        customer_id = request.user.get('UserID')

        if not order_id:
            return fail_response(None, '订单ID不能为空', 40000)

        # 验证订单属于该顾客且状态为已接单
        check_query = "SELECT DeliveryStatus FROM orders WHERE OrderID = %s AND CustomerID = %s"
        order_row = execute_query(conn, check_query, (order_id, customer_id), fetch_one=True)
        if not order_row:
            return fail_response(None, '订单不存在或无权操作', 40300)

        if order_row[0] not in ('已接单',):
            return fail_response(None, f'当前状态"{order_row[0]}"不可取消', 40000)

        update_query = "UPDATE orders SET DeliveryStatus = '已取消' WHERE OrderID = %s"
        execute_query(conn, update_query, (order_id,))

        return success_response(None, '取消成功')
    except Exception as e:
        current_app.logger.error(f"取消订单错误: {e}")
        return fail_response(None, f'取消失败: {str(e)}', 50000)


@order_bp.route('/order/assign', methods=['POST'])
@token_required
@role_required('商家')
def assign_delivery():
    """商家为订单指派配送员"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        order_id = data.get('orderId')
        deliveryman_id = data.get('deliverymanId')
        merchant_id = request.user.get('UserID')

        if not all([order_id, deliveryman_id]):
            return fail_response(None, '订单ID和配送员ID不能为空', 40000)

        # 验证订单属于该商家且状态为已接单
        check_query = "SELECT DeliveryStatus, CustomerID FROM orders WHERE OrderID = %s AND MerchantID = %s"
        order_row = execute_query(conn, check_query, (order_id, merchant_id), fetch_one=True)
        if not order_row:
            return fail_response(None, '订单不存在或无权操作', 40300)
        if order_row[0] != '已接单':
            return fail_response(None, '该订单已指派或已完成', 40000)

        # 验证配送员存在且空闲
        dm_check = "SELECT WorkStatus FROM deliveryman WHERE UserID = %s"
        dm_row = execute_query(conn, dm_check, (deliveryman_id,), fetch_one=True)
        if not dm_row:
            return fail_response(None, '配送员不存在', 40400)
        if dm_row[0] != '空闲':
            return fail_response(None, '该配送员当前不可用', 40000)

        # 获取顾客电话
        customer_id = order_row[1]
        phone_query = "SELECT Phone FROM user WHERE UserID = %s"
        phone_row = execute_query(conn, phone_query, (customer_id,), fetch_one=True)
        customer_phone = phone_row[0] if phone_row else None

        # 清理可能残留的旧配送记录（取消后重新指派的情况）
        delete_old = "DELETE FROM logistics WHERE OrderID = %s"
        execute_query(conn, delete_old, (order_id,))

        # 创建配送记录（触发器会自动更新配送员状态和订单状态）
        insert_logistics = """
            INSERT INTO logistics (OrderID, DeliverymanID, EstimatedTime, IsDelivered, CustomerPhone)
            VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 30 MINUTE), FALSE, %s)
        """
        execute_query(conn, insert_logistics, (order_id, deliveryman_id, customer_phone))

        return success_response(None, '指派成功')
    except Exception as e:
        current_app.logger.error(f"指派配送员错误: {e}")
        return fail_response(None, f'指派失败: {str(e)}', 50000)


@order_bp.route('/order/deliver', methods=['POST'])
@token_required
@role_required('配送员')
def confirm_delivery():
    """配送员确认送达"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        order_id = data.get('orderId')
        deliveryman_id = request.user.get('UserID')

        if not order_id:
            return fail_response(None, '订单ID不能为空', 40000)

        # 验证配送记录
        check_query = "SELECT IsDelivered FROM logistics WHERE OrderID = %s AND DeliverymanID = %s"
        log_row = execute_query(conn, check_query, (order_id, deliveryman_id), fetch_one=True)
        if not log_row:
            return fail_response(None, '配送记录不存在或无权操作', 40300)
        if log_row[0]:
            return fail_response(None, '该订单已送达', 40000)

        # 更新送达状态（触发器会自动更新订单状态和配送员状态）
        update_query = "UPDATE logistics SET IsDelivered = TRUE WHERE OrderID = %s"
        execute_query(conn, update_query, (order_id,))

        return success_response(None, '确认送达成功')
    except Exception as e:
        current_app.logger.error(f"确认送达错误: {e}")
        return fail_response(None, f'操作失败: {str(e)}', 50000)


@order_bp.route('/order/update-address', methods=['POST'])
@token_required
@role_required('顾客')
def update_order_address():
    """顾客修改订单收货地址（仅限已接单状态）"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        order_id = data.get('orderId')
        address_id = data.get('addressId')
        customer_id = request.user.get('UserID')

        if not all([order_id, address_id]):
            return fail_response(None, '订单ID和地址ID不能为空', 40000)

        # 验证订单属于该顾客且状态为已接单
        check_query = "SELECT DeliveryStatus FROM orders WHERE OrderID = %s AND CustomerID = %s"
        order_row = execute_query(conn, check_query, (order_id, customer_id), fetch_one=True)
        if not order_row:
            return fail_response(None, '订单不存在或无权操作', 40300)
        if order_row[0] != '已接单':
            return fail_response(None, '当前状态不可修改地址', 40000)

        # 验证地址属于该顾客
        addr_check = "SELECT AddressID FROM address WHERE AddressID = %s AND CustomerID = %s"
        addr_exists = execute_query(conn, addr_check, (address_id, customer_id), fetch_one=True)
        if not addr_exists:
            return fail_response(None, '收货地址无效', 40000)

        # 更新订单地址
        update_query = "UPDATE orders SET AddressID = %s WHERE OrderID = %s"
        execute_query(conn, update_query, (address_id, order_id))

        return success_response(None, '地址修改成功')
    except Exception as e:
        current_app.logger.error(f"修改订单地址错误: {e}")
        return fail_response(None, f'修改失败: {str(e)}', 50000)
