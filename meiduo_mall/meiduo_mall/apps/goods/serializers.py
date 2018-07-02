from rest_framework import serializers
from drf_haystack.serializers import HaystackSerializer

from .models import SKU, GoodsCategory, GoodsChannel
from .search_indexes import SKUIndex


class SKUSerializer(serializers.ModelSerializer):
    """序列化器SKU模型"""

    class Meta:
        model = SKU
        # 指定序列化（输出）字段
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


class SKUIndexSerializer(HaystackSerializer):
    """
    SKU索引结果数据序列化器
    """
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')


class CategorySerializer(serializers.ModelSerializer):
    """
    类别序列化器
    """
    class Meta:
        model = GoodsCategory
        fields = ('id', 'name')


class ChannelSerializer(serializers.ModelSerializer):
    """
    频道序列化器
    """
    category = CategorySerializer()

    class Meta:
        model = GoodsChannel
        fields = ('category', 'url')