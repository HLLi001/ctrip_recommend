"""
专门检查 python-dotenv 库的脚本
"""

import sys
import subprocess
import importlib

def check_python_dotenv():
    """专门检查 python-dotenv 库"""
    print("=" * 50)
    print("   python-dotenv 库专项检查")
    print("=" * 50)
    
    # 方法1: 使用 pip 检查
    print("\n1. 使用 pip 检查安装状态:")
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'show', 'python-dotenv'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ pip 确认 python-dotenv 已安装")
            # 提取版本信息
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.replace('Version:', '').strip()
                    print(f"   版本: {version}")
        else:
            print("❌ pip 显示 python-dotenv 未安装")
            print(f"   错误信息: {result.stderr}")
    except Exception as e:
        print(f"❌ pip 检查失败: {e}")
    
    # 方法2: 尝试直接导入
    print("\n2. 尝试直接导入:")
    try:
        import dotenv
        print("✅ 可以导入 dotenv 模块")
        
        # 检查具体功能
        from dotenv import load_dotenv
        print("✅ 可以导入 load_dotenv 函数")
        
        # 测试基本功能
        load_dotenv()  # 不传参数，只是测试函数是否存在
        print("✅ load_dotenv 函数可调用")
        
        # 获取版本
        if hasattr(dotenv, '__version__'):
            print(f"   模块版本: {dotenv.__version__}")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
    except Exception as e:
        print(f"⚠️  导入成功但功能异常: {e}")
    
    # 方法3: 使用 importlib 检查
    print("\n3. 使用 importlib 检查:")
    try:
        spec = importlib.util.find_spec("dotenv")
        if spec is not None:
            print("✅ importlib 找到 dotenv 模块")
            print(f"   模块位置: {spec.origin}")
        else:
            print("❌ importlib 未找到 dotenv 模块")
    except Exception as e:
        print(f"❌ importlib 检查失败: {e}")
    
    # 方法4: 检查 sys.path 中的模块
    print("\n4. 检查 sys.path 中的模块:")
    found = False
    for path in sys.path:
        try:
            if 'dotenv' in path.lower():
                print(f"   找到相关路径: {path}")
                found = True
        except:
            pass
    
    if not found:
        print("   在 sys.path 中未找到明显相关的 dotenv 路径")

def check_import_alternative_names():
    """检查可能的替代导入名"""
    print("\n5. 检查替代导入名:")
    alternative_names = ['dotenv', 'python_dotenv', 'python.dotenv']
    
    for name in alternative_names:
        try:
            module = importlib.import_module(name)
            print(f"✅ 可以导入: {name}")
            print(f"   模块: {module}")
        except ImportError as e:
            print(f"❌ 无法导入 {name}: {e}")

if __name__ == "__main__":
    check_python_dotenv()
    check_import_alternative_names()
    
    print("\n" + "=" * 50)
    print("检查完成！")
    print("=" * 50)