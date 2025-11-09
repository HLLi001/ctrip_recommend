# spiders/models.py
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SightInfo:
    """景点信息数据模型"""
    name: str                    # 景点名称
    rating: float               # 评分
    address: str               # 地址
    introduction: str          # 介绍
    review_count: int          # 评论数
    url: str                   # 原始URL
    city: str = ""            # 所在城市
    tags: List[str] = None     # 标签
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
    
    def to_dict(self):
        """转换为字典，便于JSON序列化"""
        return {
            'name': self.name,
            'rating': self.rating,
            'address': self.address,
            'introduction': self.introduction,
            'review_count': self.review_count,
            'url': self.url,
            'city': self.city,
            'tags': self.tags
        }

@dataclass
class Review:
    """用户评论数据模型"""
    sight_name: str           # 景点名称
    user_name: str           # 用户名
    rating: float            # 用户评分
    content: str             # 评论内容
    date: str               # 评论日期
    
    def to_dict(self):
        return {
            'sight_name': self.sight_name,
            'user_name': self.user_name,
            'rating': self.rating,
            'content': self.content,
            'date': self.date
        }