# utils/file_storage.py
import json
import csv
import os
import logging
from datetime import datetime
from config import config

class FileStorage:
    """文件存储管理器 - 增强版"""
    
    def __init__(self):
        self.data_dir = config.DATA_DIR
        self.logger = logging.getLogger('file_storage')
        
    def save_sights_to_json(self, sights_data, filename=None):
        """保存景点数据到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sights_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            # 转换为可序列化的字典列表
            data_to_save = [sight.to_dict() if hasattr(sight, 'to_dict') else sight 
                           for sight in sights_data]
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功保存 {len(sights_data)} 条景点数据到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存JSON文件失败: {e}")
            return None
    
    def save_sights_to_csv(self, sights_data, filename=None):
        """保存景点数据到CSV文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sights_data_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if not sights_data:
                self.logger.warning("没有数据可保存")
                return None
            
            # 获取字段名
            if hasattr(sights_data[0], 'to_dict'):
                sample_data = sights_data[0].to_dict()
            else:
                sample_data = sights_data[0]
            
            fieldnames = list(sample_data.keys())
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for sight in sights_data:
                    if hasattr(sight, 'to_dict'):
                        writer.writerow(sight.to_dict())
                    else:
                        writer.writerow(sight)
            
            self.logger.info(f"成功保存 {len(sights_data)} 条景点数据到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存CSV文件失败: {e}")
            return None
    
    def save_reviews_to_json(self, reviews_data, filename=None):
        """保存评论数据到JSON文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_data_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(reviews_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"成功保存 {len(reviews_data)} 条评论数据到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存评论JSON文件失败: {e}")
            return None
    
    def save_reviews_to_csv(self, reviews_data, filename=None):
        """保存评论数据到CSV文件"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reviews_data_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            if not reviews_data:
                self.logger.warning("没有评论数据可保存")
                return None
            
            fieldnames = ['sight_name', 'user_name', 'rating', 'content', 'review_time']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(reviews_data)
            
            self.logger.info(f"成功保存 {len(reviews_data)} 条评论数据到: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"保存评论CSV文件失败: {e}")
            return None
    
    def clean_sight_data(self, sights_data):
        """清洗景点数据"""
        cleaned_data = []
        seen_names = set()
        
        for sight in sights_data:
            # 转换为字典格式
            if hasattr(sight, 'to_dict'):
                data = sight.to_dict()
            else:
                data = sight
            
            # 数据验证
            if not self.is_valid_sight_data(data):
                continue
                
            # 去重（基于名称）
            if data['name'] in seen_names:
                continue
            seen_names.add(data['name'])
            
            # 数据标准化
            data = self.normalize_sight_data(data)
            cleaned_data.append(data)
        
        return cleaned_data
    
    def is_valid_sight_data(self, data):
        """验证景点数据有效性"""
        # 名称不能为空
        if not data.get('name') or data['name'] == '未知':
            return False
        
        # 评分在合理范围内
        rating = data.get('rating', 0)
        if rating < 0 or rating > 5:
            return False
        
        # 评论数不能为负数
        if data.get('review_count', 0) < 0:
            return False
        
        return True
    
    def normalize_sight_data(self, data):
        """标准化景点数据"""
        # 清理名称
        data['name'] = data['name'].strip()
        
        # 确保评分为浮点数
        data['rating'] = float(data.get('rating', 0))
        
        # 确保评论数为整数
        data['review_count'] = int(data.get('review_count', 0))
        
        # 清理地址
        if data.get('address'):
            data['address'] = data['address'].strip()
        
        # 清理介绍
        if data.get('introduction'):
            data['introduction'] = data['introduction'].strip()[:500]  # 限制长度
        
        return data
    
    def load_sights_from_json(self, filename):
        """从JSON文件加载景点数据"""
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.info(f"从 {filepath} 加载了 {len(data)} 条数据")
            return data
            
        except Exception as e:
            self.logger.error(f"加载JSON文件失败: {e}")
            return []
    
    def get_recent_data_files(self):
        """获取最近的数据文件"""
        json_files = [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
        
        all_files = []
        for file in json_files + csv_files:
            filepath = os.path.join(self.data_dir, file)
            mtime = os.path.getmtime(filepath)
            all_files.append((file, mtime))
        
        # 按修改时间排序
        all_files.sort(key=lambda x: x[1], reverse=True)
        return [file[0] for file in all_files]