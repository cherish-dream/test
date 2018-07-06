from rest_framework import serializers
from django.utils import timezone # 读取本项目中配置的市区的时间，datetime类型的
from decimal import Decimal
from django_redis import get_redis_connection
from django.db import transaction

from goods.models import SKU
from .models import OrderInfo,OrderGoods


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
        # 读取用户传入的地址和支付方式信息
        address = validated_data.get('address')
        pay_method = validated_data.get('pay_method')

        # 读取登录的user
        user = self.context['request'].user

        # 生成order_id 20180705120121000000001
        # timezone.now() = datetime类型的
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)

        # 使用with，选中需要被当做事务处理的代码
        with transaction.atomic():
            # 在这里创建一个保存点，如果回滚，就回滚到此
            save_id = transaction.savepoint()

            # 暴力回滚
            try:
                # 保存订单基本信息 OrderInfo
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user = user,
                    address = address,
                    total_count = 0,
                    total_amount = Decimal('0'), # 传数字和数字字符串都想
                    freight = Decimal('10.00'),
                    pay_method = pay_method,
                    status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method==OrderInfo.PAY_METHODS_ENUM['ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 从redis读取购物车中被勾选的商品信息
                redis_conn = get_redis_connection('carts')
                # 读取全部的购物车数据 {b'1':b'10', b'2':b'20'}
                redis_cart = redis_conn.hgetall('cart_%s' % user.id)
                # 读取被勾选的购物车数据sku_id ; selected == [b'1']
                selected = redis_conn.smembers('selected_%s' % user.id)
                # 构造要支付的新的字典
                carts = {}
                for sku_id in selected:
                    # carts = {'1':'10'}
                    carts[int(sku_id)] = int(redis_cart[sku_id])

                # 读取出被勾选的商品的sku_id列表
                sku_ids = carts.keys()
                # 遍历购物车中被勾选的商品信息 ：carts是购物车中被勾选的商品
                for sku_id in sku_ids:

                    # 下单成功：库存满足条件，要购买的商品数量小于库存，并且在更新新的库存时原始库存没有被更改
                    # result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)

                    # 下单成功：即使在更新新的库存时，发现原始的库存被更改了，但是，被更改后的库存数量依然大于用户要购买的数量
                    # if result == 0:
                    #     continue

                    # 下单失败：直到库存不足才算下单失败

                    while True:
                        # 获取sku对象
                        sku = SKU.objects.get(id=sku_id)

                        # 读取原始的库存
                        origin_stock = sku.stock # 15
                        origin_sales = sku.sales

                        sku_count = carts[sku_id]
                        # 判断库存 
                        if sku_count > origin_stock:
                            # 回滚到保存点
                            transaction.savepoint_rollback(save_id)
                            raise serializers.ValidationError('库存不足')

                        # 模拟网络延迟 # 15 --> 14
                        import time
                        time.sleep(5)

                        # 减少库存，增加销量 SKU 
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 读取新的库存和销量
                        new_stock = origin_stock - sku_count # 8
                        new_sales = origin_sales + sku_count

                        # 乐观锁更新库存和销量
                        result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
                        if result == 0:
                            continue

                        # 修改SPU销量
                        sku.goods.sales += sku_count
                        sku.goods.save()

                        # 保存订单商品信息 OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku = sku,
                            count = sku_count,
                            price = sku.price
                        )

                        # 累加计算总数量和总价
                        order.total_count += sku_count
                        order.total_amount += (sku.price * sku_count)

                        # 下单成功就跳出while循环，继续for循环，取出下一个商品
                        break

                # 最后加入邮费和保存订单信息
                order.total_amount += order.freight
                order.save()

            except serializers.ValidationError:
                # 不需要回滚，因为在判断库存时使用过了
                raise
            except Exception:
                # 回滚
                transaction.savepoint_rollback(save_id)
                raise

            # 如果成功就提交
            transaction.savepoint_commit(save_id)

            # 清除购物车中已结算的商品(待续)

            return order