# test_config.py - 增强版配置验证
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from config import config
import pymysql

def test_database_connection():
    """测试数据库连接"""
    try:
        db_config = config.get_database_config()
        connection = pymysql.connect(**db_config)
        connection.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"❌ 数据库连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知数据库错误: {e}")
        return False

def test_directories():
    """测试目录创建"""
    required_dirs = [
        config.DATA_DIR,
        config.LOG_DIR, 
        config.DATABASE_DIR
    ]
    
    all_ok = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"✅ 目录存在: {directory}")
        else:
            print(f"❌ 目录缺失: {directory}")
            all_ok = False
            
    return all_ok

def test_config_values():
    """测试配置值合理性"""
    issues = []
    
    if config.REQUEST_DELAY < 0.1:
        issues.append("请求延迟太短，可能被封IP")
    
    if config.MAX_RETRIES < 1:
        issues.append("重试次数至少为1")
        
    if config.MAX_SIGHTS > 1000:
        issues.append("爬取数量过多，建议分批进行")
    
    return issues

def main():
    """主测试函数"""
    print("🔧 综合配置测试开始")
    print("=" * 50)
    
    # 1. 显示配置信息
    print(config)
    
    # 2. 测试数据库连接
    print("\n📊 数据库连接测试:")
    db_ok = test_database_connection()
    
    # 3. 测试目录
    print("\n📁 目录结构测试:")
    dirs_ok = test_directories()
    
    # 4. 配置值检查
    print("\n⚙️ 配置合理性检查:")
    issues = test_config_values()
    if issues:
        for issue in issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ 所有配置值合理")
    
    # 5. 总结报告
    print("\n" + "=" * 50)
    print("📋 测试总结报告:")
    
    if db_ok and dirs_ok and not issues:
        print("🎉 所有测试通过！可以开始运行项目")
    else:
        print("❌ 发现一些问题，请先修复：")
        if not db_ok:
            print("   - 检查数据库配置和网络连接")
        if not dirs_ok:
            print("   - 检查文件权限")
        if issues:
            print("   - 调整不合理的配置值")
        
        print("\n💡 建议：修复问题后重新运行此测试")

if __name__ == "__main__":
    main()