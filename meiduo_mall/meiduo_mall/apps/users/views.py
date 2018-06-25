from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from . import serializers
# Create your views here.


# url(r'^email/$', views.EmailView.as_view()),
class EmailView(UpdateAPIView):
    """添加邮件的后端"""

    # 指定序列化器
    serializer_class = serializers.EmailSerializer
    # 验证用户是否登录
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# url(r'^user/$', views.UserDetailView.as_view()),
class UserDetailView(RetrieveAPIView):
    """提供登录用户的详情信息"""

    # 指定序列化器
    serializer_class = serializers.UserDetailSerializer

    # 验证当前是否是登录状态
    # IsAuthenticated : 会根据DRF配置的身份验证系统进行身份的验证，判断是否是登录的状态
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """返回当前登录用户的信息
        能够通过permission_classes的验证，说明是登录用户在访问视图
        """
        return self.request.user


# url(r'^users/$', views.UserView.as_view()),
# class UserView(GenericAPIView, CreateModelMixin):
class UserView(CreateAPIView):
    """注册"""

    serializer_class = serializers.CreateUserSerializer


# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """
    手机号数量
    """
    def get(self, request, mobile):
        """
        获取指定手机号数量
        """
        count = User.objects.filter(mobile=mobile).count()

        data = {
            'mobile': mobile,
            'count': count
        }

        return Response(data)


# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """
    用户名数量
    """
    def get(self, request, username):
        """
        获取指定用户名数量
        """
        count = User.objects.filter(username=username).count()

        data = {
            'username': username,
            'count': count
        }

        return Response(data)
