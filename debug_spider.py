import sys
import os

# 添加路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'utils'))

from spiders.ctrip_spider import CtripSpider

def main():
    spider = CtripSpider()
    
    # 测试几个已知的景点URL
    test_urls = [
        "https://you.ctrip.com/sight/beijing1/229.html",  # 故宫
        "https://you.ctrip.com/sight/beijing1/231.html",  # 天坛
        "https://you.ctrip.com/sight/shanghai2/633.html", # 东方明珠
    ]
    
    for url in test_urls:
        spider.debug_parse_page(url)
        input("\n按回车继续测试下一个...")

if __name__ == "__main__":
    main()