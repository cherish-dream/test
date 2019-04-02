from rest_framework import serializers

from .models import Area


class AreasSerializer(serializers.ModelSerializer):
    """父集输出Area模型类中的数据"""

    class Meta:
        # 指定查询集数据来源的模型类
        model = Area
        # 指定输出的字段
        fields = ('id', 'name')


class SubsAreasSerializer(serializers.ModelSerializer):
    """子集输出Area模型类中的数据"""

    # 关联
    subs = AreasSerializer(many=True, read_only=True)

    class Meta:
        # 指定查询集数据来源的模型类
        model = Area
        # 指定输出的字段
        fields = ('id', 'name', 'subs')

