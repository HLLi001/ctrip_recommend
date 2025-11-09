import os
from dotenv import load_dotenv

class Config:
    """安全配置加载类"""
    
    def __init__(self):
        # 加载 .env 文件
        load_dotenv()
        
        # 数据库配置
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = int(os.getenv('DB_PORT', 3306))
        self.DB_USER = os.getenv('DB_USER', 'root')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD', '')  # 🔐 从.env安全读取
        self.DB_NAME = os.getenv('DB_NAME', 'ctrip_recommend')
        
        # 验证必要配置
        self._validate_config()
    
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

# 创建全局配置实例
config = Config()