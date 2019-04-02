from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from .models import Area
from . import serializers
# Create your views here.

# GET /areas/
# GET /areas/<pk>/
class AreasViewSet(CacheResponseMixin, ReadOnlyModelViewSet):
    """提供省市区三级联动的数据
    list:返回列表数据（省级数据）
    retrieve:返回的那个对象数据（子集数据）
    """

    # 列表行为不分页
    pagination_class = None

    # 指定输出的输入查询集的来源
    # queryset = Area.objects.all()
    def get_queryset(self):
        if self.action == 'list':
            # 提供父集数据的查询集
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    # 指定序列化器
    # serializer_class = ''
    def get_serializer_class(self):
        """重写获取序列化器的方法：分别为list和retrieve行为指定不同的序列化器"""
        if self.action == 'list':
            return serializers.AreasSerializer
        else:
            return serializers.SubsAreasSerializer

