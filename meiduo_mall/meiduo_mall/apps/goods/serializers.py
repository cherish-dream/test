from rest_framework import serializers

from .models import SKU


class SKUSerializer(serializers.ModelSerializer):
    """序列化器SKU模型"""

    class Meta:
        model = SKU
        # 指定序列化（输出）字段
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')