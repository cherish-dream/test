from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action

from . import serializers
from . import constants
from . import serializers
# Create your views here.


# /browse_histories/
class UserBrowseHistoryView(mixins.CreateModelMixin, GenericAPIView):
    """用户浏览记录"""

    # 指定权限
    permission_classes = [IsAuthenticated]
    # 指定序列化器：为了将保存也在序列化器中实现，所以加入了CreateModelMixin
    serializer_class = serializers.AddUserBrowseHistorySerializer

    def post(self, request):
        # 接受参数sku_id
        # 校验参数
        # 保存sku_id
        # 响应：传入request，内部带有POST请求的请求体
        return self.create(request)


    # def get(self, request):
    #     """查询用户浏览记录"""
    #     pass


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put'], detail=True)
    def status(self, request, pk=None, address_id=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None, address_id=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
class VerifyEmailView(APIView):
    """邮件验证"""

    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message':'缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token，返回user
        user = User.check_verify_email_token(token)
        if not user:
            return Response({'message': '无效的token'}, status=status.HTTP_400_BAD_REQUEST)

        # 拿到user后，将user的email_active设置为True
        user.email_active = True
        user.save()

        return Response({'message':'OK'})


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
