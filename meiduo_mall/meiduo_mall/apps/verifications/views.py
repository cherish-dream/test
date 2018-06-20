from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse


# Create your views here.


# url('^image_codes/(?P<image_code_id>[\w-]+)/$', views.ImageCodeView.as_view()),
class ImageCodeView(APIView):
    """提供图片验证码"""

    def get(self, request, image_code_id):
        # 生成图片验证码

        # 存储图片验证码的内容

        # 响应图片验证码图片数据
        return HttpResponse('image', content_type='image/jpg')


