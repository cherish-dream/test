from django.shortcuts import render
from rest_framework.views import APIView
from users.models import User
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.decorators import action
from django_redis import get_redis_connection
from rest_framework_jwt.views import ObtainJSONWebToken

from . import serializers
from . import constants
from goods.models import SKU
from goods.serializers import SKUSerializer
from carts.utils import merge_cart_cookie_to_redis
# Create your views here.


class UserAuthorizeView(ObtainJSONWebToken):
    """重写JWT的登录视图，实现调用合并购物车的方法"""

    def post(self, request, *args, **kwargs):
        """重写JWT处理登录的请求方法：在保留JWT自己的逻辑基基础之上，增加自己的购物车合并的逻辑"""

        # 为了保留本身的登录业务逻辑，需要重写父类的post方法
        response = super(UserAuthorizeView, self).post(request, *args, **kwargs)

        # 使用父类的校验用户的逻辑，得到校验后的用户细腻
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user

            # 调用自己的购物车合并的逻辑
            response = merge_cart_cookie_to_redis(request=request, response=response, user=user)

        # 响应结果
        return response


        # 以下是父类的post方法的源代码
        # serializer = self.get_serializer(data=request.data)
        #
        # if serializer.is_valid():
        #     user = serializer.object.get('user') or request.user
        #     token = serializer.object.get('token')
        #     response_data = jwt_response_payload_handler(token, user, request)
        #     response = Response(response_data)
        #     if api_settings.JWT_AUTH_COOKIE:
        #         expiration = (datetime.utcnow() +
        #                       api_settings.JWT_EXPIRATION_DELTA)
        #         response.set_cookie(api_settings.JWT_AUTH_COOKIE,
        #                             token,
        #                             expires=expiration,
        #                             httponly=True)
        #     return response
        #
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def get(self, request):
        """查询用户浏览记录
        因为也需要在这个视图中实现用户浏览记录的查询，所以父类没有选择CreateAPIView(只提供post方法)
        """
        # 获取user_id
        user_id = request.user.id
        # 获取连接都redis的对象
        redis_conn = get_redis_connection('history')
        # 查询出所有的sku_id
        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, -1)

        # 遍历所有的sku_id，查询每个sku_id对应的sku对象
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)

        # 创建序列化器；将存放了序列化数据的模型对象列表传入到序列化器中序列化，并指定为多个形式
        serializer_sku = SKUSerializer(sku_list, many=True)

        # 响应sku对象列表:serializer_sku.data == 经过序列化之后的列表数据
        return Response(serializer_sku.data)


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
