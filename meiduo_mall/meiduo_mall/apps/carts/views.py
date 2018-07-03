from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status

from . import serializers
# Create your views here.


class CartView(APIView):
    """购物车后端：增删改查"""

    def perform_authentication(self, request):
        """
        重写父类的用户验证方法，不在进入视图前就检查JWT
        保证用户未登录也可以进入下面的请求方法.登录与不登录都可以通过身份的认证
        """
        pass

    def post(self, request):
        """新增"""
        # 使用序列化器校验参数
        serializer = serializers.CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 读取校验之后的参数
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        # 判断用户是否登录
        # request.user  会去查询用户的身份信息的。如果为登录就会抛出异常或者指定为匿名用户
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录,操作redis
            redis_conn = get_redis_connection('carts')
            # 管道
            pl = redis_conn.pipeline()
            # 给购物车中的商品的数量进行增量计算
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            # 记录用户是否是勾选
            pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应结果：
            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
        else:
            # 用户未登录,操作cookie
            pass


    def get(self, request):
        """查询"""
        pass


    def put(self, request):
        """修改"""
        pass


    def delete(self, request):
        """删除"""
        pass