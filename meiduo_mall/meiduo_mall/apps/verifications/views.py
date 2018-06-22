from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from . import constants
# Create your views here.


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(APIView):
    """发送短信验证码"""

    def get(self, request, mobile):
        # 接受参数（暂时不做）
        # 校验参数（暂时不做）

        # 生成短信验证码

        # 存储短信验证码到redis

        # 发送短信验证码

        # 响应json给vue,所以需要是json数据格式，进而选择Response
        return Response({'message':'OK'})


# url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
class ImageCodeView(APIView):
    """提供图片验证码"""

    def get(self, request, image_code_id):
        # 生成图片验证码:text存储到redis数据库；image响应到用户
        text, image = captcha.generate_captcha()

        # 存储图片验证码的内容
        redis_conn = get_redis_connection('verify_codes')
        # 保存图片验证码内容到redis数据库：key expires value
        redis_conn.setex('img_%s'%image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)

        # 响应图片验证码图片数据
        return HttpResponse(image, content_type='image/jpg')


