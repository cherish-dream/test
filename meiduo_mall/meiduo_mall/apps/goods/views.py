from django.shortcuts import render
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter

from .models import SKU
from .serializers import SKUSerializer
# Create your views here.


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



