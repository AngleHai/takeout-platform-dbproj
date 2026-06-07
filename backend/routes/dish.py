from flask import Blueprint, request, current_app
from utils.db import get_db_connection, execute_query
from utils.response import success_response, fail_response
from utils.auth import token_required, role_required

dish_bp = Blueprint('dish', __name__)


@dish_bp.route('/dish/list', methods=['GET'])
@token_required
def get_dish_list():
    """获取菜品列表，支持按商家筛选"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        merchant_id = request.args.get('merchantId')
        keyword = request.args.get('keyword')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        offset = (page - 1) * page_size

        conditions = []
        params = []

        if merchant_id:
            conditions.append("d.MerchantID = %s")
            params.append(merchant_id)
        if keyword:
            conditions.append("d.DishName LIKE %s")
            params.append(f"%{keyword}%")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        # 总数
        count_query = f"SELECT COUNT(*) FROM dish d {where_clause}"
        total = execute_query(conn, count_query, params, fetch_one=True)[0]

        # 分页查询
        query = f"""
            SELECT d.DishID, d.DishName, d.Price, d.TotalSales, d.MerchantID, m.ShopName
            FROM dish d
            JOIN merchant m ON d.MerchantID = m.UserID
            {where_clause}
            ORDER BY d.TotalSales DESC
            LIMIT %s OFFSET %s
        """
        params.extend([page_size, offset])
        rows = execute_query(conn, query, params, fetch_all=True)

        dishes = [{
            'dishId': r[0],
            'dishName': r[1],
            'price': float(r[2]),
            'totalSales': r[3],
            'merchantId': r[4],
            'shopName': r[5]
        } for r in rows]

        return success_response({'list': dishes, 'total': total})
    except Exception as e:
        current_app.logger.error(f"获取菜品列表错误: {e}")
        return fail_response(None, '服务器内部错误', 50000)


@dish_bp.route('/dish/add', methods=['POST'])
@token_required
@role_required('商家')
def add_dish():
    """商家添加菜品"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        dish_name = data.get('dishName')
        price = data.get('price')
        merchant_id = request.user.get('UserID')

        if not dish_name or price is None:
            return fail_response(None, '菜品名称和价格不能为空', 40000)

        if float(price) <= 0:
            return fail_response(None, '价格必须大于0', 40000)

        # 生成菜品ID
        id_query = "SELECT MAX(DishID) FROM dish"
        max_id = execute_query(conn, id_query, fetch_one=True)
        if max_id and max_id[0]:
            new_num = int(max_id[0][1:]) + 1
        else:
            new_num = 1
        new_dish_id = f"D{new_num:07d}"

        insert_query = "INSERT INTO dish (DishID, DishName, Price, TotalSales, MerchantID) VALUES (%s, %s, %s, 0, %s)"
        execute_query(conn, insert_query, (new_dish_id, dish_name, price, merchant_id))

        return success_response({'dishId': new_dish_id}, '添加成功')
    except Exception as e:
        current_app.logger.error(f"添加菜品错误: {e}")
        return fail_response(None, f'添加失败: {str(e)}', 50000)


@dish_bp.route('/dish/update', methods=['POST'])
@token_required
@role_required('商家')
def update_dish():
    """商家修改菜品信息"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        dish_id = data.get('dishId')
        merchant_id = request.user.get('UserID')

        if not dish_id:
            return fail_response(None, '菜品ID不能为空', 40000)

        # 验证该菜品属于当前商家
        check_query = "SELECT DishID FROM dish WHERE DishID = %s AND MerchantID = %s"
        exists = execute_query(conn, check_query, (dish_id, merchant_id), fetch_one=True)
        if not exists:
            return fail_response(None, '菜品不存在或无权修改', 40300)

        updates = []
        params = []
        if 'dishName' in data:
            updates.append("DishName = %s")
            params.append(data['dishName'])
        if 'price' in data:
            updates.append("Price = %s")
            params.append(data['price'])

        if not updates:
            return fail_response(None, '无更新内容', 40000)

        params.append(dish_id)
        update_query = f"UPDATE dish SET {', '.join(updates)} WHERE DishID = %s"
        execute_query(conn, update_query, params)

        return success_response(None, '修改成功')
    except Exception as e:
        current_app.logger.error(f"修改菜品错误: {e}")
        return fail_response(None, f'修改失败: {str(e)}', 50000)


@dish_bp.route('/dish/delete', methods=['POST'])
@token_required
@role_required('商家')
def delete_dish():
    """商家删除菜品"""
    conn = get_db_connection()
    if not conn:
        return fail_response(None, '数据库连接失败', 50000)

    try:
        data = request.get_json()
        dish_id = data.get('dishId')
        merchant_id = request.user.get('UserID')

        if not dish_id:
            return fail_response(None, '菜品ID不能为空', 40000)

        # 验证该菜品属于当前商家
        check_query = "SELECT DishID FROM dish WHERE DishID = %s AND MerchantID = %s"
        exists = execute_query(conn, check_query, (dish_id, merchant_id), fetch_one=True)
        if not exists:
            return fail_response(None, '菜品不存在或无权删除', 40300)

        # 检查是否有未完成订单包含此菜品
        order_check = """
            SELECT od.OrderID FROM order_dish od
            JOIN orders o ON od.OrderID = o.OrderID
            WHERE od.DishID = %s AND o.DeliveryStatus IN ('已接单', '配送中')
        """
        active_orders = execute_query(conn, order_check, (dish_id,), fetch_all=True)
        if active_orders:
            return fail_response(None, '该菜品有未完成订单，暂不能删除', 40000)

        delete_query = "DELETE FROM dish WHERE DishID = %s"
        execute_query(conn, delete_query, (dish_id,))

        return success_response(None, '删除成功')
    except Exception as e:
        current_app.logger.error(f"删除菜品错误: {e}")
        return fail_response(None, f'删除失败: {str(e)}', 50000)
