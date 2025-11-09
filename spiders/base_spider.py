# spiders/base_spider.py
import requests
import time
import random
import logging
from bs4 import BeautifulSoup

class BaseSpider:
    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_headers(self):
        """获取随机请求头 - 不使用外部依赖"""
        user_agents = [
            # Chrome
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            
            # Firefox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13.5; rv:109.0) Gecko/20100101 Firefox/119.0',
            
            # Safari
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            
            # Edge
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Referer': 'https://you.ctrip.com/'
        }
    
    def random_delay(self, min_delay=1, max_delay=5):
        """随机延时"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def get_page(self, url, timeout=10, retry_count=3):
        """获取网页内容 - 增强版"""
        for i in range(retry_count):
            try:
                headers = self.get_headers()
                response = self.session.get(
                    url, 
                    headers=headers, 
                    timeout=timeout,
                    allow_redirects=True
                )
                response.encoding = 'utf-8'
                
                if response.status_code == 200:
                    self.logger.info(f"成功获取页面: {url}")
                    return response.text
                elif response.status_code in [403, 429]:
                    self.logger.warning(f"访问受限，状态码: {response.status_code}")
                    self.random_delay(10, 30)  # 长时间等待
                else:
                    self.logger.warning(f"请求失败，状态码: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"第{i+1}次请求超时")
            except requests.exceptions.ConnectionError:
                self.logger.warning(f"第{i+1}次连接错误")
            except Exception as e:
                self.logger.error(f"第{i+1}次请求失败: {str(e)}")
                
            if i < retry_count - 1:
                wait_time = 2 ** i  # 指数退避
                self.logger.info(f"等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)
                    
        self.logger.error(f"重试{retry_count}次后仍然失败: {url}")
        return None