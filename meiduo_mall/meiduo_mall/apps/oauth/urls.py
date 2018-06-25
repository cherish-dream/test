from django.conf.urls import url
from . import views


urlpatterns = [
    # 获取QQ登录扫码界面
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # 获取QQ用户的openid(用户信息)
    url(r'^qq/user/$', views.QQAuthUserView.as_view()),
]