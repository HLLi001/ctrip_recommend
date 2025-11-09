import os
from dotenv import load_dotenv

class Config:
    """安全配置加载类 - 增强版"""
    
    def __init__(self):
        # 加载 .env 文件
        load_dotenv()
        
        # ========== 数据库配置 ==========
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = int(os.getenv('DB_PORT', 3306))
        self.DB_USER = os.getenv('DB_USER', 'root')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '')  # 🔐 从.env安全读取
        self.DB_NAME = os.getenv('DB_NAME', 'ctrip_recommend')
        
        # ========== 爬虫配置 ==========
        self.REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', 1))
        self.MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
        self.TIMEOUT = int(os.getenv('TIMEOUT', 10))
        self.MAX_SIGHTS = int(os.getenv('MAX_SIGHTS', 100))
        
        # ========== 新增爬虫配置 ==========
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        self.CRAWL_REVIEWS = os.getenv('CRAWL_REVIEWS', 'False').lower() == 'true'
        self.MAX_REVIEWS_PER_SIGHT = int(os.getenv('MAX_REVIEWS_PER_SIGHT', 10))
        
        # ========== 日志配置 ==========
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_FILE = os.getenv('LOG_FILE', 'logs/spider.log')
        
        # ========== 项目路径配置 ==========
        self.BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.BASE_DIR, 'data')
        self.LOG_DIR = os.path.join(self.BASE_DIR, 'logs')
        self.DATABASE_DIR = os.path.join(self.BASE_DIR, 'database')
        self.SPIDERS_DIR = os.path.join(self.BASE_DIR, 'spiders')
        self.UTILS_DIR = os.path.join(self.BASE_DIR, 'utils')
        self.TEMP_DIR = os.path.join(self.BASE_DIR, 'temp')
        
        # 验证必要配置
        self._validate_config()
        # 创建必要目录
        self._create_directories()
    
    def _validate_config(self):
        """验证必要配置是否存在"""
        if not self.DB_PASSWORD:
            raise ValueError("数据库密码未配置！请检查 .env 文件")
        
        required_configs = {
            'DB_HOST': self.DB_HOST,
            'DB_USER': self.DB_USER, 
            'DB_PASSWORD': self.DB_PASSWORD,
            'DB_NAME': self.DB_NAME
        }
        
        for key, value in required_configs.items():
            if not value:
                raise ValueError(f"配置 {key} 不能为空！")
    
    def _create_directories(self):
        """创建项目所需的目录结构"""
        directories = [
            self.DATA_DIR,
            self.LOG_DIR,
            self.DATABASE_DIR,
            self.SPIDERS_DIR,
            self.UTILS_DIR,
            self.TEMP_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ 目录已就绪: {directory}")
    
    def get_database_config(self):
        """获取数据库连接配置字典"""
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME,
            'charset': 'utf8mb4',
            'autocommit': True,
        }
    
    def get_spider_config(self):
        """获取爬虫配置字典"""
        return {
            'request_delay': self.REQUEST_DELAY,
            'max_retries': self.MAX_RETRIES,
            'timeout': self.TIMEOUT,
            'max_sights': self.MAX_SIGHTS,
            'debug_mode': self.DEBUG_MODE,
            'crawl_reviews': self.CRAWL_REVIEWS,
            'max_reviews_per_sight': self.MAX_REVIEWS_PER_SIGHT,
        }
    
    def __str__(self):
        """打印配置信息（隐藏密码）"""
        return f"""
Config Info:
=========== 数据库配置 ===========
主机: {self.DB_HOST}
端口: {self.DB_PORT}
用户: {self.DB_USER}
数据库: {self.DB_NAME}
密码: {'*' * len(self.DB_PASSWORD) if self.DB_PASSWORD else '未设置'}

=========== 爬虫配置 ===========
请求延迟: {self.REQUEST_DELAY}秒
最大重试: {self.MAX_RETRIES}次
超时时间: {self.TIMEOUT}秒
最大景点数: {self.MAX_SIGHTS}个
调试模式: {self.DEBUG_MODE}
爬取评论: {self.CRAWL_REVIEWS}
每景点最大评论数: {self.MAX_REVIEWS_PER_SIGHT}

=========== 路径配置 ===========
项目根目录: {self.BASE_DIR}
数据目录: {self.DATA_DIR}
日志目录: {self.LOG_DIR}
        """.strip()

# 创建全局配置实例
config = Config()