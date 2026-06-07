from flask import Flask, request, g
from flask_cors import CORS
import logging

from cfg import Config
from utils.response import fail_response

# 导入蓝图
from routes.auth import auth_bp
from routes.dish import dish_bp
from routes.order import order_bp
from routes.address import address_bp
from routes.deliveryman import deliveryman_bp
from routes.admin import admin_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.logger.setLevel(logging.DEBUG)

    # CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})

    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(dish_bp, url_prefix='/api')
    app.register_blueprint(order_bp, url_prefix='/api')
    app.register_blueprint(address_bp, url_prefix='/api')
    app.register_blueprint(deliveryman_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')

    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return fail_response(None, 'API地址不存在', 40400), 404

    @app.errorhandler(500)
    def internal_error(error):
        import traceback
        traceback.print_exc()
        return fail_response(None, '服务器内部错误', 50000), 500

    # 请求结束时关闭数据库连接
    @app.teardown_appcontext
    def teardown_db(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("外卖平台管理系统 - 后端服务")
    print("运行地址: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', debug=True, port=5000)
