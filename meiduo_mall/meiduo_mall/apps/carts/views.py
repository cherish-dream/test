from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status
import base64
import pickle

from . import serializers
from goods.models import SKU
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
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行
            pl.execute()
            # 响应结果：
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 用户未登录,操作cookie
            cart_str = request.COOKIES.get('cart')
            # 判断用户是否在cookie中有购物车数据
            if cart_str:
                # 说明用户在cookie中操作过购物车数据
                # 将原始的购物车字符串转成bytes类型的字符串(二进制字符串)
                # cart_str.encode()
                # 将二进制的字符串，转换测过base64编码后的二进制字符串
                # base64.b64decode(cart_str.encode())
                # 将base64编码之后的二进制字符串转成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # {
            #     sku_id10: {
            #                   "count": 10, // 数量
            #     "selected": True // 是否勾选
            # },
            # sku_id20: {
            #     "count": 20,
            #     "selected": False
            # },
            # ...
            # }

            # 判断要添加到cookie中的购物车数据是否已存在，如果已存储就累加，反之，赋新值
            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]['count']
                count += origin_count

            # 更新字典
            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }

            # 将购物车字典写入到cookie，必须先字典转成字符串
            # 将字典进过pickle序列化为bytes
            # pickle.dumps(cart_dict)
            # 将bytes经过base64编码为二进制的字符串（二进制字典转二进制字符串）
            # base64.b64encode(pickle.dumps(cart_dict))
            # 将二进制的字符串转成字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建response
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            # 写入到cookie
            response.set_cookie('cart', cookie_cart_str)
            return response

    def get(self, request):
        """查询
        """
        # 判断用户是否登录
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            # 用户已登录,操作redis
            redis_conn = get_redis_connection('carts')
            # 查询出所有的购物车数据
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            # {
            #     b'sku_id':b'count',
            #     b'sku_id': b'count'
            # }
            cart_selected = redis_conn.smembers('selected_%s' % user.id)

            # 统一查询之后的格式为cart_dict，方便后面的查询sku的操作
            # {
            #     sku_id10: {
            #                   "count": 10, // 数量
            #     "selected": True // 是否勾选
            # },
            # sku_id20: {
            #     "count": 20,
            #     "selected": False
            # },
            # ...
            # }
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                cart_dict[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in cart_selected
                }
        else:
            # 用户未登录,操作cookie
            cart_str = request.COOKIES.get('cart')
            # 判断用户是否在cookie中有购物车数据
            if cart_str:
                # 将购物车字符串数据转成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

        # 遍历cart_dict，取出里面的所有的sku_id,用于查询出购物车数据对应的sku对象
        sku_ids = cart_dict.keys()  # sku_ids = [10,20]
        skus = SKU.objects.filter(id__in=sku_ids) # 这种写法避免便利了cart_dict字典

        # 为了在序列化的时候可以带上count和selected
        for sku in skus:
            sku.count = cart_dict[sku.id]['count']
            sku.selected = cart_dict[sku.id]['selected']

        # 创建序列化器对象，进行序列化操作
        serializer = serializers.CartSKUSerializer(skus, many=True)

        return Response(serializer.data)


    def put(self, request):
        """修改"""
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

            # 修改商品的数量:因为接口设计幂等的，所以前端传入的数量就是最终的结果，直接覆盖写入
            redis_conn.hset('cart_%s' % user.id, sku_id, count)
            # 修改商品是否勾选:如果前端传入的是已勾选，那么由于使用的是幂等的接口设计，所以直接使用selected覆盖
            if selected:
                redis_conn.sadd('selected_%s' % user.id, sku_id)
            else:
                redis_conn.srem('selected_%s' % user.id, sku_id)

            # 响应结果：修改和获取的状态码是200，新增是201，删除时204
            return Response(serializer.data)
        else:
            # 用户未登录,操作cookie
            cart_str = request.COOKIES.get('cart')
            # 判断用户是否在cookie中有购物车数据
            if cart_str:
                # 将购物车字符串数据转成字典
                cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
            else:
                cart_dict = {}

            # 因为接口设计为幂等的，所以直接对数据进行覆盖
            cart_dict[sku_id] = {
                'count':count,
                'selected':selected
            }

            # 将字典转成bytes,再将bytes转成base64的bytes,最后将bytes转字符串
            cookie_cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()

            # 创建响应对象
            response = Response(serializer.data)

            # 响应结果并将购物车数据写入到cookie
            response.set_cookie('cart', cookie_cart_str)
            return response


    def delete(self, request):
        """删除"""
        pass