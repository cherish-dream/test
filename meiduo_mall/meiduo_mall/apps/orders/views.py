from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_redis import get_redis_connection
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from goods.models import SKU
from . import serializers
# Create your views here.

class OrderSettlementView(APIView):
    """
    订单结算（去结算）
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        获取
        """
        user = request.user

        # 从购物车中获取用户勾选要结算的商品信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('cart_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)

        # 存储被勾选的商品信息
        cart = {}
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]

        # 运费
        # float 1.23 ==> 123 * 10 ^ -2 (123乘以10的负二次方)  1.29999999
        # Decimal()   1.23  ==> 1     23   1.23

        freight = Decimal('10.00')

        serializer = serializers.OrderSettlementSerializer({'freight': freight, 'skus': skus})
        return Response(serializer.data)


class CommitOrderView(CreateAPIView):
    """提交订单："""

    # 指定权限
    permission_classes = [IsAuthenticated]
    # 指定序列化器
    serializer_class = serializers.CommitOrderSerializer
