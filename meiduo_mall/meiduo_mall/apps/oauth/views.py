from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_jwt.views import api_settings

from .utils import OAuthQQ
from .models import OAuthQQUser
from .exceptions import QQAPIException
# Create your views here.


# url(r'^qq/user/$', views.QQAuthUserView.as_view()), 
# 是QQ服务器将用户重定向到oauth_callback.html页面时发起的
class QQAuthUserView(APIView):
    """用户扫码登录的回调处理"""

    def get(self, request):
        # 提取code请求参数
        code = request.query_params.get('code')
        if not code:
            return Response({'message':'缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建oauth工具对象
        oauth = OAuthQQ()

        try:
            # 使用code向QQ服务器请求access_token
            access_token = oauth.get_access_token(code)

            # 使用access_token向QQ服务器请求openid
            openid = oauth.get_openid(access_token)
        except QQAPIException:
            return Response({'message':'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用openid查询该QQ用户是否在美多商城中绑定过用户
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定美多商城用户，创建用户并绑定到openid

        else:
            # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
            user = oauth_user.user

            # 生成JWT——token
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            return Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })


#  url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
# 点击QQ登录标签发起的请求
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
