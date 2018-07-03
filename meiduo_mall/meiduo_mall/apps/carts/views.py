from django.shortcuts import render
from rest_framework.views import APIView

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