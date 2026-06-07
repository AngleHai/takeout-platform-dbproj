import os
import datetime


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'takeout_secret_key_change_in_prod')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=24)

    # 数据库配置
    DB_HOST = "localhost"
    DB_USER = "root"
    DB_PASSWORD = "root123"
    DB_DATABASE = "takeout"

    # CORS 配置
    CORS_ORIGINS = ["http://localhost:5173", "http://localhost:3000"]
