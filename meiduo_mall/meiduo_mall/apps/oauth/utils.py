from django.conf import settings
from urllib.parse import urlencode,parse_qs
from urllib.request import urlopen
import json
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from .exceptions import QQAPIException
from . import constants


import logging
# 日志记录器
logger = logging.getLogger('django')


class OAuthQQ(object):
    """QQ登录的工具类"""

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        """初始化的构造方法：接受参数"""
        self.client_id = client_id or settings.QQ_CLIENT_ID
        self.client_secret = client_secret or settings.QQ_CLIENT_SECRET
        self.redirect_uri = redirect_uri or settings.QQ_REDIRECT_URI
        self.state = state or settings.QQ_STATE


    def get_qq_login_url(self):

        # 准备url：记得自己补充问号
        login_url = 'https://graph.qq.com/oauth2.0/authorize?'

        # 准备参数
        params = {
            'response_type':'code', # 表示获取code
            'client_id':self.client_id, # 应用的id
            'redirect_uri':self.redirect_uri, # 扫码后的回调界面
            'state':self.state, # QQ登录成功后跳转界面
            'scope':'get_user_info' # 表示扫码是为了回去QQ用户信息
        }

        # 拼接QQQ登录的url
        # url = 'https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xx&redirect_uri=xxstate=xx&scope=xx'
        login_url += urlencode(params)

        return login_url


    def get_access_token(self, code):

        # 准备url
        url = 'https://graph.qq.com/oauth2.0/token?'

        # 准备参数
        params = {
            'grant_type':'authorization_code',
            'client_id':self.client_id,
            'client_secret':self.client_secret,
            'code':code,
            'redirect_uri':self.redirect_uri
        }

        # 拼接地址
        url += urlencode(params)

        try:
            # 使用code向QQ服务器发送请求获取access_token
            response = urlopen(url)
            # 获取响应提二进制
            response_data = response.read()
            # access_token=FE04************************CCE2&expires_in=7776000&refresh_token=88E4************************BE14
            response_str = response_data.decode()
            # 转响应字典
            response_dict = parse_qs(response_str)
            # 获取access_token:被存放列表中，只有access_token一个元素==response_dict.get('access_token')==[access_token]
            access_token = response_dict.get('access_token')[0]
        except Exception as e:
            logger.error(e)
            raise QQAPIException('获取access_token失败')

        return access_token


    def get_openid(self, access_token):
        """
        使用access_token向QQ服务器请求openid
        openid 是我们、用户在注册个人QQ账号时，QQ服务器给分配的用户的唯一标识
        :param access_token: 上一步获取的access_token
        :return: open_id
        """

        # 准备url
        url = 'https://graph.qq.com/oauth2.0/me?access_token=' + access_token

        # 美多向QQ服务器发送请求获取openid
        response_str = ''
        try:
            response = urlopen(url)
            response_str = response.read().decode()

            # 返回的数据 callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} )\n;
            response_dict = json.loads(response_str[10:-4])
            # 获取openid
            openid = response_dict.get('openid')
        except Exception as e:
            # 如果有异常，QQ服务器返回 "code=xxx&msg=xxx"
            data = parse_qs(response_str)
            logger.error(e)
            raise QQAPIException('code=%s msg=%s' % (data.get('code'), data.get('msg')))

        return openid


    @staticmethod
    def generate_save_user_token(openid):
        """
        生成保存用户数据的token
        :param openid: 用户的openid
        :return: token
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        data = {'openid': openid}
        token = serializer.dumps(data)
        return token.decode()


    @staticmethod
    def check_save_user_token(token):
        """
        检验保存用户数据的token
        :param token: token
        :return: openid or None
        """
        serializer = Serializer(settings.SECRET_KEY, expires_in=constants.SAVE_QQ_USER_TOKEN_EXPIRES)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            return data.get('openid')



