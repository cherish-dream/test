from rest_framework import serializers

from goods.models import SKU
from .models import OrderInfo


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class OrderSettlementSerializer(serializers.Serializer):
    """
    订单结算数据序列化器
    """
    # float 1.23 ==> 123 * 10 ^ -2  --> 1.299999999
    # Decimal  1.23    1    23
    # max_digits 一共多少位；decimal_places：小数点保留几位
    freight = serializers.DecimalField(label='运费', max_digits=10, decimal_places=2)
    skus = CartSKUSerializer(many=True)


class CommitOrderSerializer(serializers.ModelSerializer):
    """提交订单"""

    class Meta:
        model = OrderInfo
        # order_id ：输出；address 和 pay_method : 输入
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        # 指定address 和 pay_method 为输出
        extra_kwargs = {
            'address': {
                'write_only': True,
            },
            'pay_method': {
                'write_only': True,
            }
        }


    def create(self, validated_data):
        """提交订单时，保存订单数据（OrderInfo）和订单商品数据(OrderGoods)"""

        # 获取当前保存订单时需要的信息

        # 保存订单基本信息 OrderInfo

        # 从redis读取购物车中被勾选的商品信息

        # 遍历购物车中被勾选的商品信息
            # 获取sku对象

            # 判断库存 

            # 减少库存，增加销量 SKU 

            # 修改SPU销量

            # 保存订单商品信息 OrderGoods

            # 累加计算总数量和总价

        # 最后加入邮费和保存订单信息

        # 清除购物车中已结算的商品

        pass