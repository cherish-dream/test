from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from alipay import AliPay
from django.conf import settings
import os

from orders.models import OrderInfo
# Create your views here.


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
