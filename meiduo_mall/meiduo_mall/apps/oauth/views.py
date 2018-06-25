from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import OAuthQQ
# Create your views here.


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """提供QQ登录界面的URL"""

    def get(self, request):

        # 创建oauth工具对象
        oauth = OAuthQQ()

        # 调用获取QQ登录界面的URL的工具方法
        login_url =  oauth.get_qq_login_url()

        # 返回QQ登录界面的URL给浏览器
        return Response({'login_url':login_url})
