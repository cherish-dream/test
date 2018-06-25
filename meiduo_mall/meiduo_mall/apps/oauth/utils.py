from django.conf import settings
from urllib.parse import urlencode,parse_qs
from urllib.request import urlopen

from .exceptions import QQAPIException


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



