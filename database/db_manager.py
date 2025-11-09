import pymysql
from utils.config import config  # 🔐 从安全配置模块导入

class DatabaseManager:
    """安全的数据库连接管理"""
    
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """使用安全配置连接数据库"""
        try:
            self.connection = pymysql.connect(
                host=config.DB_HOST,           # 🔐 从配置读取
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASSWORD,   # 🔐 密码不硬编码
                database=config.DB_NAME,
                charset='utf8mb4'
            )
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise