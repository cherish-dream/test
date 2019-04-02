from celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
from celery_tasks.main import celery_app


# 使用装饰器将send_sms_code装饰成异步任务，并起别名
@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """发送短信异步任务"""

    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], constants.SMS_SEND_TEMPLATE_ID)
