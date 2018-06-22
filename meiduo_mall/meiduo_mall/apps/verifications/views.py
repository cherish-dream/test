from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
import random

from . import constants
from libs.yuntongxun.sms import CCP
from . import serializers
from celery_tasks.sms.tasks import send_sms_code
# Create your views here.


# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """发送短信验证码"""

    # 指定序列化器
    serializer_class = serializers.ImageCodeCheckSerializer

    def get(self, request, mobile):
        # DRF实现参数的校验+校验图片验证码

        # 获取序列化器对象:需要将text和image_code_id这两个查询字符串传入到序列化器对象中进行校验
        serializer = self.get_serializer(data=request.query_params)
        # 开启校验
        serializer.is_valid(raise_exception=True)

        # 生成短信验证码
        sms_code = '%06d' % random.randint(0, 999999)

        # 存储短信验证码到redis
        redis_conn = get_redis_connection('verify_codes')
        # redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        #
        # # 记录发送短信的标记
        # redis_conn.setex('sned_flag_%s' % mobile, constants.SMS_CODE_REDIS_INTERVAL , 1)

        # redis管道，可以将多个redis指令集成到一起执行，不用多次访问redis数据库
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)

        # 记录发送短信的标记
        pl.setex('send_flag_%s' % mobile, constants.SMS_CODE_REDIS_INTERVAL, 1)
        # 开启执行
        pl.execute()

        # 发送短信验证码
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SMS_SEND_TEMPLATE_ID)

        # 执行异步任务:delay将延迟异步任务发送到redis
        send_sms_code.delay(mobile, sms_code)

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


