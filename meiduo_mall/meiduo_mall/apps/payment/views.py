from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from django.conf import settings
import os

from orders.models import OrderInfo
from .models import Payment
# Create your views here.


# payment/status/?支付宝参数
class PaymentStatusView(APIView):
    """对接支付宝的订单状态查询:修改订单状态"""
    #  /pay_success.html?charset=utf-8&out_trade_no=20180707005303000000001&method=alipay.trade.page.pay.return&total_amount=3798.00&sign=g6odZxEwm4qqW5SqFXbwZOVGRF3AkIIc24Luo9jgXn68h3JxtskR7fcDxVb5%2BgoZurq7cRSDpbQqqdCckA9PlNGvzmvlUZWwzWJpDNqk%2FxSQjlGPfKNZ7Vnh1%2BdYpCS0jX0G14E%2F1i81n7GT%2BqkLcnBoTIxp1xzTyU8vwkwQcCPjhDysFleSRLGSHu1YJjzmOzRcNxKstk39wQmNQxRUgcq8vbqfBDwCoLH2JiMu93rUZ52iYH9aWSeYX79S8rr3SZaS%2FwoyTTP1IRGpvRE81AVGFLAlJL4QtdgglUg41rDihEyuqnms3bBoO5%2BKLe9RjIqqYSikX1irIEWU3Ww9Tg%3D%3D&trade_no=2018070721001004510200532761&auth_app_id=2016082100308405&version=1.0&app_id=2016082100308405&sign_type=RSA2&seller_id=2088102172481561&timestamp=2018-07-07+10%3A40%3A01

    def put(self, request):
        # 读取支付宝重定向到美多商城的请求参数(查询字符串)
        query_dict = request.query_params  # QueryDict 一键一值，一键多值 get() getlist()
        # 将QueryDict类型的对象，转成python字典
        data = query_dict.dict()
        # 读取支付宝的签名：并将它从字典中移除
        signature = data.pop("sign")

        # 创建对接支付宝的SDK对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 验证订单的重定向是否从支付宝过来的
        success = alipay.verify(data, signature)
        if success:
            # 查询订单成功:取出美多商城维护的订单号和支付宝自己生成的交易流水号
            order_id = data.get('out_trade_no')
            trade_id = data.get('trade_no')

            # 本质工作：保存支付宝交易流水号，并跟自己的订单号绑定
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_id
            )

            # 本质工作：修改订单的状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(status=OrderInfo.ORDER_STATUS_ENUM["UNSEND"])

            # 响应支付结果
            return Response({'trade_id':trade_id})

        else:
            # 查询订单失败
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)


# /orders/(?P<order_id>\d+)/payment/
class PaymentView(APIView):
    """对接支付宝的支付"""

    # 必须登录才能访问
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        # 接受并校验order_id
        try:
            # 查询出当前登录用户的待支付的订单
            order = OrderInfo.objects.get(order_id=order_id, user=request.user, pay_method=OrderInfo.PAY_METHODS_ENUM["ALIPAY"], status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return Response({'message': '订单信息有误'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建对接支付宝支付接口的对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.ALIPAY_DEBUG  # 默认False
        )

        # 调用支付宝的支付接口（进入到支付宝登录界面）
        # 正式环境：电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 测试环境：电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url="http://www.meiduo.site:8080/pay_success.html",
        )

        # 响应支付宝登录界面给用户（可以登录并完成支付）
        # 正式环境：电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        # 测试环境：电脑网站支付，需要跳转到https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return Response({'alipay_url':alipay_url})
