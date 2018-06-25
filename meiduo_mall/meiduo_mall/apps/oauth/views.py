from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .utils import OAuthQQ
# Create your views here.


# url(r'^qq/user/$', views.QQAuthUserView.as_view()), 
class QQAuthUserView(APIView):
    """用户扫码登录的回调处理"""
    def get(self, request):
        # 提取code请求参数
        # 使用code向QQ服务器请求access_token
        # 使用access_token向QQ服务器请求openid
        # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
        # 如果openid没绑定美多商城用户，创建用户并绑定到openid
        pass


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
class QQAuthURLView(APIView):
    """提供QQ登录界面的URL"""

    def get(self, request):

        # 获取next
        next = request.query_params.get('next')

        # 创建oauth工具对象
        oauth = OAuthQQ(state=next)

        # 调用获取QQ登录界面的URL的工具方法
        login_url =  oauth.get_qq_login_url()

        # 返回QQ登录界面的URL给浏览器
        return Response({'login_url':login_url})
