from rest_framework import serializers

from goods.models import SKU


class CartSerializer(serializers.Serializer):
    """购物车的序列化器"""

    # 定义字段
    sku_id = serializers.IntegerField(label='商品 sku 编号', min_value=1)
    count = serializers.IntegerField(label='商品数量', min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate(self, attrs):
        sku_id = attrs['sku_id']
        count = attrs['count']

        # 判断sku_id是否存在
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('sku id 不存在')

        # 判断库存
        if count > sku.stock:
            raise serializers.ValidationError('库存不足')

        return attrs


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id', 'count', 'name', 'default_image_url', 'price', 'selected')


class CartDeleteSerializer(serializers.Serializer):
    """
    删除购物车数据序列化器
    """
    sku_id = serializers.IntegerField(label='商品id', min_value=1)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value