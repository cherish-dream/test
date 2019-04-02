from django.shortcuts import render
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.filters import OrderingFilter
from drf_haystack.viewsets import HaystackViewSet
from rest_framework.response import Response

from .models import SKU, GoodsCategory
from .serializers import SKUSerializer,SKUIndexSerializer, ChannelSerializer, CategorySerializer
# Create your views here.


class CategoryView(GenericAPIView):
    """
    商品列表页的面包屑导航
    """
    queryset = GoodsCategory.objects.all()

    def get(self, request, pk=None):
        ret = dict(
            cat1='',
            cat2='',
            cat3=''
        )
        category = self.get_object()
        if category.parent is None:
            # 当前类别为一级类别
            ret['cat1'] = ChannelSerializer(category.goodschannel_set.all()[0]).data
        elif category.goodscategory_set.count() == 0:
            # 当前类别为三级
            ret['cat3'] = CategorySerializer(category).data
            cat2 = category.parent
            ret['cat2'] = CategorySerializer(cat2).data
            ret['cat1'] = ChannelSerializer(cat2.parent.goodschannel_set.all()[0]).data
        else:
            # 当前类别为二级
            ret['cat2'] = CategorySerializer(category).data
            ret['cat1'] = ChannelSerializer(category.parent.goodschannel_set.all()[0]).data

        return Response(ret)


class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer


# /categories/(?P<category_id>\d+)/skus?page=xxx&page_size=xxx&ordering=xxx
class SKUListView(ListAPIView):
    """商品列表：排序和分页"""

    # 指定查询集:因为我们展示商品的列表是分为商品的分类展示的，如果已经下架不需要展示，所以以上数据需要自己过滤
    # queryset = SKU.objects.all()

    # 指定序列化器
    serializer_class = SKUSerializer

    # 指定过滤排序的后端
    filter_backends = [OrderingFilter]

    # 指定过滤排序的字段
    # create_time == 默认 price==价格  sales==人气
    ordering_fields = ('create_time', 'price', 'sales')

    def get_queryset(self):
        # 从路径中获取商品列表所要展示的分类
        # http://127.0.0.1:8080/list.html?cat=115
        category_id = self.kwargs.get('category_id')
        return SKU.objects.filter(category_id=category_id, is_launched=True)



