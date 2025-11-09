# main.py
import logging
import os
import sys
import time

# 修复导入路径 - 添加utils目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = os.path.join(current_dir, 'utils')
sys.path.append(utils_dir)

# 现在可以导入config了
from config import config
from spiders.ctrip_spider import CtripSpider
from file_storage import FileStorage

def setup_logging():
    """配置日志"""
    os.makedirs(config.LOG_DIR, exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(config.LOG_DIR, 'ctrip_spider.log'), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def validate_data_quality(sights_data):
    """验证数据质量"""
    logger = logging.getLogger('main')
    
    if not sights_data:
        logger.warning("没有数据可验证")
        return
    
    total = len(sights_data)
    
    # 统计各项数据的完整性
    name_complete = sum(1 for s in sights_data if s.get('name') and s.get('name') != '未知')
    rating_complete = sum(1 for s in sights_data if s.get('rating', 0) > 0)
    address_complete = sum(1 for s in sights_data if s.get('address') and s.get('address') != '未知')
    intro_complete = sum(1 for s in sights_data if s.get('introduction'))
    
    logger.info("📊 数据质量报告:")
    logger.info(f"   总数据量: {total}")
    logger.info(f"   名称完整率: {name_complete}/{total} ({name_complete/total*100:.1f}%)")
    logger.info(f"   评分完整率: {rating_complete}/{total} ({rating_complete/total*100:.1f}%)")
    logger.info(f"   地址完整率: {address_complete}/{total} ({address_complete/total*100:.1f}%)")
    logger.info(f"   介绍完整率: {intro_complete}/{total} ({intro_complete/total*100:.1f}%)")

def main():
    """主程序 - 增强版"""
    setup_logging()
    logger = logging.getLogger('main')
    
    logger.info("=" * 50)
    logger.info("开始携程旅行数据爬取（增强版）...")
    logger.info("=" * 50)
    
    try:
        # 初始化存储
        storage = FileStorage()
        
        # 开始爬虫
        spider = CtripSpider()
        
        # 可选：先进行小规模测试
        if config.DEBUG_MODE:
            logger.info("调试模式：先测试少量数据")
            test_sights = spider.crawl_all_sights(max_sights=10)
            if test_sights:
                logger.info("测试成功，开始完整爬取")
            else:
                logger.error("测试失败，请检查爬虫配置")
                return
        
        logger.info(f"计划爬取最多 {config.MAX_SIGHTS} 个景点")
        
        # 爬取景点数据
        sights_data = spider.crawl_all_sights(max_sights=config.MAX_SIGHTS)
        
        if sights_data:
            # 数据清洗
            cleaned_data = storage.clean_sight_data(sights_data)
            logger.info(f"数据清洗后剩余 {len(cleaned_data)} 个有效景点")
            
            # 数据质量验证
            validate_data_quality(cleaned_data)
            
            # 保存数据
            json_file = storage.save_sights_to_json(cleaned_data)
            csv_file = storage.save_sights_to_csv(cleaned_data)
            
            logger.info("=" * 50)
            logger.info(f"爬虫完成！成功爬取 {len(cleaned_data)} 个景点数据")
            if json_file:
                logger.info(f"JSON文件: {json_file}")
            if csv_file:
                logger.info(f"CSV文件: {csv_file}")
            logger.info("=" * 50)
            
            # 显示数据统计
            show_data_stats(cleaned_data)
            
            # 可选：爬取评论数据
            if config.CRAWL_REVIEWS:
                logger.info("开始爬取评论数据...")
                all_reviews = []
                for sight in cleaned_data[:config.MAX_REVIEWS_PER_SIGHT]:  # 限制数量，避免请求过多
                    reviews = spider.get_sight_reviews(sight['url'], max_reviews=10)
                    for review in reviews:
                        review['sight_name'] = sight['name']
                    all_reviews.extend(reviews)
                    time.sleep(2)  # 评论请求间隔
                
                if all_reviews:
                    review_json_file = storage.save_reviews_to_json(all_reviews)
                    review_csv_file = storage.save_reviews_to_csv(all_reviews)
                    logger.info(f"成功爬取 {len(all_reviews)} 条评论")
                    if review_json_file:
                        logger.info(f"评论JSON文件: {review_json_file}")
                    if review_csv_file:
                        logger.info(f"评论CSV文件: {review_csv_file}")
            
        else:
            logger.warning("没有爬取到任何数据，请检查爬虫配置或网站结构")
        
    except Exception as e:
        logger.error(f"程序执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())

def show_data_stats(sights_data):
    """显示数据统计信息 - 移除城市信息"""
    if not sights_data:
        return
    
    logger = logging.getLogger('main')
    
    # 基本统计
    total_sights = len(sights_data)
    
    # 评分统计
    ratings = [sight.get('rating', 0) for sight in sights_data if sight.get('rating', 0) > 0]
    if ratings:
        avg_rating = sum(ratings) / len(ratings)
        max_rating = max(ratings)
        min_rating = min(ratings)
    else:
        avg_rating = max_rating = min_rating = 0
    
    # 评论数统计
    review_counts = [sight.get('review_count', 0) for sight in sights_data]
    total_reviews = sum(review_counts)
    avg_reviews = total_reviews / total_sights if total_sights > 0 else 0
    
    # 数据完整性统计
    name_complete = sum(1 for s in sights_data if s.get('name') and s.get('name') != '未知')
    rating_complete = sum(1 for s in sights_data if s.get('rating', 0) > 0)
    address_complete = sum(1 for s in sights_data if s.get('address') and s.get('address') != '未知')
    intro_complete = sum(1 for s in sights_data if s.get('introduction'))
    
    logger.info("📊 详细数据统计:")
    logger.info(f"   总景点数: {total_sights}")
    logger.info(f"   平均评分: {avg_rating:.2f} (最高: {max_rating:.1f}, 最低: {min_rating:.1f})")
    logger.info(f"   总评论数: {total_reviews} (平均: {avg_reviews:.1f})")
    
    logger.info("✅ 数据完整性:")
    logger.info(f"   名称完整率: {name_complete}/{total_sights} ({name_complete/total_sights*100:.1f}%)")
    logger.info(f"   评分完整率: {rating_complete}/{total_sights} ({rating_complete/total_sights*100:.1f}%)")
    logger.info(f"   地址完整率: {address_complete}/{total_sights} ({address_complete/total_sights*100:.1f}%)")
    logger.info(f"   介绍完整率: {intro_complete}/{total_sights} ({intro_complete/total_sights*100:.1f}%)")
    
    # 评分分布
    rating_ranges = {'5星': 0, '4星': 0, '3星': 0, '2星': 0, '1星': 0}
    for rating in ratings:
        if rating >= 4.5:
            rating_ranges['5星'] += 1
        elif rating >= 3.5:
            rating_ranges['4星'] += 1
        elif rating >= 2.5:
            rating_ranges['3星'] += 1
        elif rating >= 1.5:
            rating_ranges['2星'] += 1
        else:
            rating_ranges['1星'] += 1
    
    logger.info("⭐ 评分分布:")
    for range_name, count in rating_ranges.items():
        if count > 0:
            percentage = (count / len(ratings)) * 100
            logger.info(f"   {range_name}: {count}个景点 ({percentage:.1f}%)")

if __name__ == "__main__":
    main()