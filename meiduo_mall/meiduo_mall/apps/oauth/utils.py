from django.conf import settings
from urllib.parse import urlencode


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


    # def get_access_token(self):
    #     pass