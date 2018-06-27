from rest_framework import serializers
from django_redis import get_redis_connection
from redis import RedisError
import logging


# 日志记录器
logger = logging.getLogger('django')


class ImageCodeCheckSerializer(serializers.Serializer):
    """校验图片验证码序列化器"""

    # 指定要校验的字段: (字段名字)image_code_id 必须和外界传入(data=request.query_params)的同名:
    # image_code_id = serializers.UUIDField()
    # text = serializers.CharField(min_length=4,max_length=4)

    def validate(self, attrs):
        """对比图片验证码"""
        # 获取经过字段校验之后的image_code_id和text
        image_code_id = attrs['image_code_id']
        text = attrs['text']

        # 使用image_code_id查询出redis中的图片验证码
        redis_conn = get_redis_connection('verify_codes')
        image_code_server = redis_conn.get('img_%s' % image_code_id)
        # 判断服务器存储的图片验证码是否有效，有可能过期了
        if image_code_server is None:
            raise serializers.ValidationError('无效的图片验证码')

        # 删除Redis中存储的图片验证码，防止暴力测试
        # 提示：如果不在这里捕获异常，会被DRF捕获到，然后直接returnn,那么后续的对比逻辑无法正常执行
        # 提示：自己捕获异常的原因为，删除图片验证码是附带的逻辑，删除是否成功不重要，不能让他的异常影响了主线逻辑
        try:
            redis_conn.delete('img_%s' % image_code_id)
        except RedisError as e:
            logger.error(e)

        # 使用text和服务器存储的image_code_server进行对比
        image_code_server = image_code_server.decode() # 因为py3中redis数据库读取的数据类型是bytes；py2读取的是原始数据
        # 执行对比：需要同步大小写
        if text.lower() != image_code_server.lower():
            raise serializers.ValidationError('输入图片验证码有误')

        # 不能在这里删除Redis中存储的图片验证码，因为如果每次对比失败，就会无法删除

        # 校验60s内是否重复发送短信
        # 学习如何在序列化器中获取请求传入到视图中的额外的数据
        mobile = self.context['view'].kwargs['mobile']
        send_flag = redis_conn.get('send_flag_%s' % mobile)
        if send_flag:
            raise serializers.ValidationError('发送短信验证码过于频繁')

        return attrs
