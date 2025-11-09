import re
import json
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base_spider import BaseSpider
from .models import SightInfo

class CtripSpider(BaseSpider):
    """携程旅行景点数据爬虫"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://you.ctrip.com"
        self.sight_list_urls = [
            "https://you.ctrip.com/sight/beijing1/s0-p1.html",  # 北京景点
            "https://you.ctrip.com/sight/shanghai2/s0-p1.html", # 上海景点
            "https://you.ctrip.com/sight/guangzhou152/s0-p1.html", # 广州景点
            "https://you.ctrip.com/sight/shenzhen26/s0-p1.html" # 深圳景点
        ]
        
    def normalize_url(self, url):
        """标准化URL，确保使用主站点地址"""
        # 如果已经是完整URL，直接返回
        if url.startswith('http'):
            # 确保使用https和正确的主域名
            url = url.replace('http://', 'https://')
            url = url.replace('gs.ctrip.com/html5/you', 'you.ctrip.com')
            return url
        else:
            # 相对路径，添加基础URL
            return 'https://you.ctrip.com' + url
    
    def is_valid_sight_url(self, url):
        """检查URL是否为有效的景点详情页 - 进一步优化"""
        # 排除列表页、活动页等非景点页面
        invalid_patterns = [
            '/s0-p',           # 列表分页
            '/sight/.*/s0-p',  # 城市列表页
            'javascript',      # JavaScript链接
            '/allvision',      # 全景页面
            '/food',           # 美食页面
            '/shopping',       # 购物页面
            '/activity',       # 活动页面
            '/sight/.*/0\.html',  # ID为0的页面（通常是专题页）
            'gs.ctrip.com',    # 移动端简化页面
            'html5/you',       # HTML5移动页面
            '?pofid='          # 推广链接
        ]
        
        for pattern in invalid_patterns:
            if pattern in url:
                return False
        
        # 只接受主站点的景点页面
        valid_domains = [
            'you.ctrip.com',
            'www.ctrip.com'
        ]
        
        # 检查是否在有效域名内
        domain_valid = any(domain in url for domain in valid_domains)
        if not domain_valid:
            return False
        
        # 必须是包含数字ID的景点页
        return re.search(r'/sight/\w+/\d+\.html', url) is not None
        
    def get_sight_list(self, max_pages=3):
        """获取景点列表页"""
        sight_links = []
        
        for base_url in self.sight_list_urls:
            self.logger.info(f"开始爬取地区: {base_url}")
            
            for page in range(1, max_pages + 1):
                url = base_url.replace('p1', f'p{page}')
                
                html = self.get_page(url)
                if html:
                    links = self.parse_sight_list(html)
                    sight_links.extend(links)
                    self.logger.info(f"第{page}页获取到{len(links)}个景点链接")
                else:
                    self.logger.warning(f"第{page}页获取失败")
                    
                self.random_delay(1, 2)
            
        return list(set(sight_links))  # 去重
    
    def parse_sight_list(self, html):
        """解析景点列表页 - 最终优化版"""
        soup = BeautifulSoup(html, 'lxml')
        sight_links = []
        
        # 查找所有链接
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href')
            if href and '/sight/' in href and '.html' in href:
                # 标准化URL
                full_url = self.normalize_url(href)
                
                # 严格过滤
                if self.is_valid_sight_url(full_url) and full_url not in sight_links:
                    sight_links.append(full_url)
                    self.logger.debug(f"找到景点链接: {full_url}")
        
        self.logger.info(f"从当前页面解析到 {len(sight_links)} 个有效景点链接")
        return sight_links
    
    def debug_page_content(self, url):
        """调试页面内容"""
        html = self.get_page(url)
        if not html:
            print(f"无法获取页面: {url}")
            return
            
        soup = BeautifulSoup(html, 'lxml')
        
        print(f"\n=== 调试页面: {url} ===")
        print(f"页面标题: {soup.title.string if soup.title else '无标题'}")
        
        # 检查所有链接
        all_links = soup.find_all('a', href=True)
        valid_links = []
        invalid_links = []
        
        print("所有包含'/sight/'的链接:")
        count = 0
        for link in all_links:
            href = link.get('href')
            if href and '/sight/' in href and count < 100:  # 检查前100个
                full_url = self.base_url + href if href.startswith('/') else href
                full_url = self.normalize_url(full_url)
                link_text = link.get_text().strip()[:30]
                
                if self.is_valid_sight_url(full_url):
                    print(f"✅ 有效景点链接: {full_url} - 文本: {link_text}")
                    valid_links.append(full_url)
                else:
                    print(f"❌ 无效链接: {full_url} - 文本: {link_text}")
                    invalid_links.append(full_url)
                count += 1
        
        # 保存HTML到文件以便分析
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n=== 统计结果 ===")
        print(f"有效景点链接: {len(valid_links)} 个")
        print(f"无效链接: {len(invalid_links)} 个")
        print(f"页面已保存到 debug_page.html")
        
        return valid_links
    
    def debug_address_elements(self, url):
        """调试地址元素 - 增强版"""
        html = self.get_page(url)
        if not html:
            print(f"无法获取页面: {url}")
            return
        
        soup = BeautifulSoup(html, 'lxml')
        
        print(f"\n=== 调试地址元素: {url} ===")
        
        # 检查所有可能包含地址的元素
        address_selectors = [
            '.sight_detail_addr',
            '.address',
            '[class*="address"]',
            '.sight_detail_info',
            '.mod_intro',
            '.detailLayout',
            '.baseInfo',
            '.sight_info',
            '.spot-address',
            '.location-info',
            '.detail-address',
            '.sight-address',
            '.text_item',
            '.text-style',
            '.content',
            '.info-item',
            '.detail-info',
            '.sight-detail-address'
        ]
        
        print("所有可能包含地址的元素:")
        for selector in address_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text().strip()
                if text and len(text) > 5 and len(text) < 200:
                    print(f"  - {selector}: {text}")
        
        # 检查所有包含"地址"关键词的元素
        print("\n包含'地址'关键词的元素:")
        for elem in soup.find_all(string=re.compile('地址')):
            parent = elem.parent
            if parent:
                full_text = parent.get_text().strip()
                if len(full_text) > 10:
                    print(f"  - {parent.name}.{'.'.join(parent.get('class', []))}: {full_text}")
        
        # 检查所有包含"位置"关键词的元素
        print("\n包含'位置'关键词的元素:")
        for elem in soup.find_all(string=re.compile('位置')):
            parent = elem.parent
            if parent:
                full_text = parent.get_text().strip()
                if len(full_text) > 10:
                    print(f"  - {parent.name}.{'.'.join(parent.get('class', []))}: {full_text}")
        
        # 测试解析方法
        print(f"\n解析结果: {self.parse_address(soup)}")
    
    def get_sight_detail(self, url):
        """获取景点详细信息"""
        html = self.get_page(url)
        if not html:
            return None
            
        return self.parse_sight_detail(html, url)
    
    def parse_sight_detail(self, html, url):
        """解析景点详情页 - 改进版"""
        soup = BeautifulSoup(html, 'lxml')
        
        try:
            # 改进的景点名称解析
            name = self.parse_sight_name(soup)
            if name == '未知' or '攻略' in name or '旅游' in name or '携程' in name:
                self.logger.warning(f"跳过无效景点名称: {name}")
                return None
            
            # 改进的评分解析
            rating = self.parse_rating(soup)
            
            # 改进的地址解析
            address = self.parse_address(soup)
            
            # 介绍解析
            introduction = self.parse_introduction(soup)
            
            # 评论数解析
            review_count = self.parse_review_count(soup)
            
            # 城市信息
            city = self.parse_city_from_url(url)
            
            # 更新日志输出，移除城市信息
            self.logger.info(f"成功解析景点: {name} - 评分: {rating} - 地址: {address[:20]}... - 评论数: {review_count}")
            
            return SightInfo(
                name=name,
                rating=rating,
                address=address,
                introduction=introduction,
                review_count=review_count,
                url=url,
                city=city
            )
            
        except Exception as e:
            self.logger.error(f"解析景点详情失败: {str(e)}")
            return None
    
    def parse_sight_name(self, soup):
        """解析景点名称 - 改进版"""
        # 尝试多种选择器
        name_selectors = [
            'h1[class*="detail"]',
            '.detailTitle',
            '.sight_detail_cntitle',
            'h1'
        ]
        
        for selector in name_selectors:
            elem = soup.select_one(selector)
            if elem:
                name = elem.get_text().strip()
                # 过滤掉明显不是景点名称的文本
                if (name and 
                    len(name) < 50 and 
                    '攻略' not in name and 
                    '旅游' not in name and
                    '携程' not in name and
                    '推荐' not in name and
                    '大全' not in name and
                    '打卡' not in name):
                    return name
        
        return '未知'
    
    def parse_rating(self, soup):
        """解析评分 - 改进版"""
        # 携程评分的选择器
        rating_selectors = [
            '.score .textscore',      # 评分文本
            '.avgScore',              # 平均分
            '[class*="score"] span',  # 评分span
            '.biz_summary .score',    # 商业评分
            '.commentScore',          # 评论评分
            '.comment_score'          # 评论分数
        ]
        
        for selector in rating_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text().strip()
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    rating = float(numbers[0])
                    if 1 <= rating <= 5:  # 有效评分范围
                        return rating
        
        return 0.0
    
    def parse_address(self, soup):
        """解析地址 - 精确版"""
        # 首先尝试精确的选择器
        precise_selectors = [
            '.sight_detail_addr',
            '.sight-address .content',
            '.spot-address .text',
            '.detail-address',
            '[data-b*="address"]',
            '.address .text'
        ]
        
        for selector in precise_selectors:
            elem = soup.select_one(selector)
            if elem:
                address = elem.get_text().strip()
                if self.is_valid_address(address):
                    return self.clean_address(address)
        
        # 尝试查找包含"地址"关键词的元素
        address_keywords = ['地址', '位置', '地点']
        for keyword in address_keywords:
            # 查找包含关键词的元素
            elements = soup.find_all(string=re.compile(keyword))
            for elem in elements:
                parent = elem.parent
                if parent:
                    # 获取父元素的完整文本
                    full_text = parent.get_text().strip()
                    
                    # 尝试从文本中提取地址部分
                    address_match = re.search(rf'{keyword}[:：]\s*([^\n\r]+)', full_text)
                    if address_match:
                        address = address_match.group(1).strip()
                        if self.is_valid_address(address):
                            return self.clean_address(address)
                    
                    # 如果没有明确的分隔符，尝试获取父元素后面的文本
                    next_sibling = parent.find_next_sibling()
                    if next_sibling:
                        sibling_text = next_sibling.get_text().strip()
                        if self.is_valid_address(sibling_text):
                            return self.clean_address(sibling_text)
        
        # 尝试从结构化数据中提取
        address = self.extract_address_from_structured_data(soup)
        if address and self.is_valid_address(address):
            return address
        
        # 最后尝试从页面文本中搜索
        all_text = soup.get_text()
        address_patterns = [
            r'地址[:：]\s*([^\n\r]{10,80})',
            r'位置[:：]\s*([^\n\r]{10,80})',
            r'地点[:：]\s*([^\n\r]{10,80})',
            r'位于([^\n\r]{10,80})',
            r'坐落于([^\n\r]{10,80})',
            r'地处([^\n\r]{10,80})'
        ]
        
        for pattern in address_patterns:
            matches = re.findall(pattern, all_text)
            for match in matches:
                if self.is_valid_address(match):
                    return self.clean_address(match)
        
        return '未知'
    
    def is_valid_address(self, address):
        """检查地址是否有效"""
        if not address or len(address) < 5 or len(address) > 200:
            return False
        
        # 排除明显不是地址的文本
        invalid_patterns = [
            r'母婴室',
            r'卫生间',
            r'停车场',
            r'营业时间',
            r'门票',
            r'电话',
            r'网址',
            r'邮箱',
            r'微信公众号',
            r'二维码',
            r'攻略',
            r'旅游',
            r'携程',
            r'推荐',
            r'大全',
            r'打卡'
        ]
        
        for pattern in invalid_patterns:
            if re.search(pattern, address):
                return False
        
        # 地址应该包含一些地理相关的词汇
        valid_patterns = [
            r'[省市县区镇乡村街道路巷号]',
            r'[东南西北]',
            r'[0-9]+号',
            r'[大学中学小学]',
            r'[公园广场景区景点]'
        ]
        
        valid_count = sum(1 for pattern in valid_patterns if re.search(pattern, address))
        return valid_count >= 1
    
    def clean_address(self, address):
        """清理地址文本"""
        # 移除多余的空格和换行
        address = re.sub(r'\s+', ' ', address).strip()
        
        # 移除地址前的标签
        address = re.sub(r'^[地址位置地点][:：]\s*', '', address)
        
        # 截断过长的地址
        if len(address) > 100:
            address = address[:100] + '...'
        
        return address
    
    def extract_address_from_structured_data(self, soup):
        """从结构化数据中提取地址"""
        # 尝试从JSON-LD数据中提取
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                json_data = json.loads(script.string)
                if isinstance(json_data, dict):
                    address = json_data.get('address')
                    if address:
                        if isinstance(address, dict):
                            # 结构化地址
                            street = address.get('streetAddress')
                            locality = address.get('addressLocality')
                            region = address.get('addressRegion')
                            if street:
                                return street
                            elif locality and region:
                                return f"{locality}{region}"
                        elif isinstance(address, str):
                            return address
            except:
                continue
        
        # 尝试从meta标签中提取
        meta_selectors = [
            'meta[name="address"]',
            'meta[name="location"]',
            'meta[property="address"]',
            'meta[property="location"]'
        ]
        
        for selector in meta_selectors:
            elem = soup.select_one(selector)
            if elem and elem.get('content'):
                content = elem.get('content')
                if self.is_valid_address(content):
                    return content
        
        return None
    
    def parse_introduction(self, soup):
        """解析景点介绍"""
        intro_selectors = [
            '.summary',
            '.introduction',
            '.sight_detail_intro',
            '.mod_intro .text_style'
        ]
        
        for selector in intro_selectors:
            elem = soup.select_one(selector)
            if elem:
                intro = elem.get_text().strip()
                if intro and len(intro) > 10:
                    return intro[:300]  # 限制长度
        
        return ''
    
    def parse_review_count(self, soup):
        """解析评论数"""
        review_selectors = [
            '.reviewCount',
            '.commentCount',
            '[class*="review"]'
        ]
        
        for selector in review_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text()
                numbers = re.findall(r'\d+', text)
                if numbers:
                    return int(numbers[0])
        
        return 0
    
    def parse_city_from_url(self, url):
        """从URL解析城市信息"""
        city_map = {
            'beijing1': '北京',
            'shanghai2': '上海', 
            'guangzhou152': '广州',
            'shenzhen26': '深圳'
        }
        
        for city_key, city_name in city_map.items():
            if city_key in url:
                return city_name
        
        # 如果URL中没有明确城市信息，尝试从域名推断
        if 'you.ctrip.com/sight/1/' in url:
            return '北京'  # 1通常代表北京
        
        return ''
    
    def get_sight_reviews(self, sight_url, max_reviews=50):
        """获取景点评论数据"""
        # 构造评论页URL（需要根据携程实际URL结构调整）
        review_url = sight_url.replace('.html', '/review.html')
        
        html = self.get_page(review_url)
        if not html:
            return []
        
        return self.parse_reviews(html, max_reviews)
    
    def parse_reviews(self, html, max_reviews):
        """解析评论数据"""
        soup = BeautifulSoup(html, 'lxml')
        reviews = []
        
        # 评论选择器（需要根据实际页面结构调整）
        review_selectors = [
            '.commentItem',
            '.review-item',
            '.comment-list li',
            '.user-comment'
        ]
        
        for selector in review_selectors:
            review_elements = soup.select(selector)
            if review_elements:
                for elem in review_elements[:max_reviews]:
                    review = self.parse_single_review(elem)
                    if review:
                        reviews.append(review)
                break
        
        return reviews
    
    def parse_single_review(self, elem):
        """解析单条评论"""
        try:
            # 用户名
            user_name = self.parse_review_username(elem)
            # 评分
            rating = self.parse_review_rating(elem)
            # 评论内容
            content = self.parse_review_content(elem)
            # 评论时间
            review_time = self.parse_review_time(elem)
            
            if user_name and content:
                return {
                    'user_name': user_name,
                    'rating': rating,
                    'content': content,
                    'review_time': review_time
                }
        except Exception as e:
            self.logger.warning(f"解析评论失败: {e}")
        
        return None
    
    def parse_review_username(self, elem):
        """解析评论用户名"""
        username_selectors = [
            '.user-name',
            '.username',
            '.name',
            '[class*="user"]'
        ]
        
        for selector in username_selectors:
            username_elem = elem.select_one(selector)
            if username_elem:
                return username_elem.get_text().strip()
        
        return '匿名用户'
    
    def parse_review_rating(self, elem):
        """解析评论评分"""
        rating_selectors = [
            '.rating',
            '.score',
            '[class*="rating"]',
            '[class*="score"]'
        ]
        
        for selector in rating_selectors:
            rating_elem = elem.select_one(selector)
            if rating_elem:
                text = rating_elem.get_text().strip()
                numbers = re.findall(r'\d+\.?\d*', text)
                if numbers:
                    rating = float(numbers[0])
                    if 1 <= rating <= 5:
                        return rating
        
        return 0.0
    
    def parse_review_content(self, elem):
        """解析评论内容"""
        content_selectors = [
            '.content',
            '.comment-content',
            '.text',
            '.review-text'
        ]
        
        for selector in content_selectors:
            content_elem = elem.select_one(selector)
            if content_elem:
                content = content_elem.get_text().strip()
                if content and len(content) > 5:
                    return content[:500]  # 限制长度
        
        return ''
    
    def parse_review_time(self, elem):
        """解析评论时间"""
        time_selectors = [
            '.time',
            '.date',
            '.review-time',
            '[class*="time"]'
        ]
        
        for selector in time_selectors:
            time_elem = elem.select_one(selector)
            if time_elem:
                time_text = time_elem.get_text().strip()
                # 尝试解析各种时间格式
                return self.normalize_time(time_text)
        
        return datetime.now().strftime('%Y-%m-%d')
    
    def normalize_time(self, time_text):
        """标准化时间格式"""
        # 处理各种时间格式，如："2023-10-01", "1天前", "2个月前"等
        try:
            # 如果是标准日期格式
            if re.match(r'\d{4}-\d{2}-\d{2}', time_text):
                return time_text
            
            # 处理相对时间
            if '天前' in time_text:
                days = int(re.findall(r'\d+', time_text)[0])
                return (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            if '月前' in time_text:
                months = int(re.findall(r'\d+', time_text)[0])
                return (datetime.now() - timedelta(days=months*30)).strftime('%Y-%m-%d')
                
        except:
            pass
        
        return time_text
    
    def crawl_all_sights(self, max_sights=100):
        """爬取所有景点信息"""
        self.logger.info("开始爬取景点列表...")
        sight_links = self.get_sight_list()
        self.logger.info(f"共获取到{len(sight_links)}个景点链接")
        
        sights_data = []
        count = 0
        
        for link in sight_links:
            if count >= max_sights:
                break
                
            sight_info = self.get_sight_detail(link)
            if sight_info and sight_info.name != '未知':
                sights_data.append(sight_info)
                count += 1
                self.logger.info(f"已爬取 {count}/{max_sights} 个景点")
            else:
                self.logger.warning(f"跳过无效景点: {link}")
                
            self.random_delay(1, 2)  # 每个景点之间延时
            
        return sights_data
    
    def debug_parse_page(self, url):
        """调试方法：详细解析单个页面"""
        html = self.get_page(url)
        if not html:
            print(f"无法获取页面: {url}")
            return
        
        soup = BeautifulSoup(html, 'lxml')
        
        print(f"\n=== 调试页面: {url} ===")
        
        # 检查所有可能的名称元素
        print("可能的名称元素:")
        name_candidates = soup.select('h1, .detailTitle, .sight_detail_cntitle, title')
        for elem in name_candidates:
            text = elem.get_text().strip()
            print(f"  - {elem.name}.{'.'.join(elem.get('class', []))}: {text}")
        
        # 检查所有可能的评分元素
        print("\n可能的评分元素:")
        rating_candidates = soup.select('[class*="score"], [class*="rating"], .avgScore, .commentScore')
        for elem in rating_candidates:
            text = elem.get_text().strip()
            print(f"  - {elem.name}.{'.'.join(elem.get('class', []))}: {text}")
        
        # 测试解析方法
        print("\n解析结果:")
        print(f"  名称: {self.parse_sight_name(soup)}")
        print(f"  评分: {self.parse_rating(soup)}")
        print(f"  地址: {self.parse_address(soup)}")
        print(f"  评论数: {self.parse_review_count(soup)}")