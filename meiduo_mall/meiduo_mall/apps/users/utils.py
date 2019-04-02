from django.contrib.auth.backends import ModelBackend
import re
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    """根据用户传入的账号查询用户"""
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            # 手机号码
            user = User.objects.get(mobile=account)
        else:
            # 用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """自定义登录验证后端，实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):

        # 使用用户名或者手机号查询用户信息
        user = get_user_by_account(username)
        # 如果user存在，校验user的密码，如果密码家宴通过，就返回user
        if user and user.check_password(password):
            return user