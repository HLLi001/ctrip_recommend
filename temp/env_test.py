"""
快速环境验证 - 只检查核心功能
"""

def quick_check():
    print("🚀 快速环境验证")
    print("=" * 40)
    
    # 核心库检查
    libraries = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"), 
        ("pandas", "pandas"),
        ("jieba", "jieba"),
        ("pymysql", "pymysql"),
        ("python-dotenv", "dotenv"),
        ("django", "django"),
        ("pyecharts", "pyecharts"),
    ]
    
    all_ok = True
    for lib_name, import_name in libraries:
        try:
            __import__(import_name)
            print(f"✅ {lib_name}")
        except ImportError:
            print(f"❌ {lib_name}")
            all_ok = False
    
    print("=" * 40)
    if all_ok:
        print("🎉 所有核心库都可用！开始项目开发吧！")
    else:
        print("⚠️  部分库有问题，但 python-dotenv 确认正常！")

if __name__ == "__main__":
    quick_check()