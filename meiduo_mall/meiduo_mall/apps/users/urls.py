from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token


urlpatterns = [
    # 校验用户名和手机号是否重复注册
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 注册
    url(r'^users/$', views.UserView.as_view()),
    # JWT辅助登录
    url(r'^authorizations/$', obtain_jwt_token),
    # 获取登录用户的详情信息
    url(r'^user/$', views.UserDetailView.as_view()),
    # 帮顶设置邮件的路由
    url(r'^email/$', views.EmailView.as_view()),
    # 验证邮件
    url(r'^emails/verification/$', views.VerifyEmailView.as_view()),
]