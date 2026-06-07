import mysql.connector
from mysql.connector import Error
from flask import current_app, g
import logging

logger = logging.getLogger(__name__)


def get_db_connection():
    """获取数据库连接，存储在 g 对象中，每个请求复用同一连接"""
    if 'db' not in g:
        try:
            conn = mysql.connector.connect(
                host=current_app.config['DB_HOST'],
                user=current_app.config['DB_USER'],
                password=current_app.config['DB_PASSWORD'],
                database=current_app.config['DB_DATABASE'],
                raise_on_warnings=False
            )
            g.db = conn
        except Error as err:
            current_app.logger.error(f"连接MySQL失败: {err}", exc_info=True)
            g.db = None
            raise
    return g.db


def execute_query(conn, query, params=None, fetch_one=False, fetch_all=False):
    """
    执行 SQL 查询。
    SELECT: 根据 fetch_one/fetch_all 返回结果
    INSERT/UPDATE/DELETE: 执行并提交
    """
    if not conn:
        raise ConnectionError("数据库连接不可用")

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())

        if query.strip().upper().startswith("SELECT") or query.strip().upper().startswith("SHOW"):
            results = cursor.fetchall()
            if fetch_one:
                return results[0] if results else None
            elif fetch_all:
                return results
            else:
                return results
        else:
            conn.commit()
            if query.strip().upper().startswith("INSERT"):
                return cursor.lastrowid
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"SQL执行失败: {e}\nQuery: {query}\nParams: {params}", exc_info=True)
        raise
    finally:
        if cursor:
            cursor.close()


def init_db():
    """检查数据库连接是否正常"""
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST if hasattr(Config, 'DB_HOST') else 'localhost',
            user='root',
            password='123456',
            database='takeout'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        logger.info("数据库连接检查通过")
    except Error as err:
        logger.error(f"数据库连接检查失败: {err}")
