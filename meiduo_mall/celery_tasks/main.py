# celery启动入口
from celery import Celery


# 为celery使用django配置文件进行设置
import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'


# 创建celery客户端,并起别名（没有实际意义）
celery_app = Celery('meiduo')

# 加载配置:让客户端和worker知道broker的存在
celery_app.config_from_object('celery_tasks.config')

# 自动将异步任务注册到celery_app
# 提示：不需要指向tasks.py;因为celery默认回去寻找tasks.py同名的文件
celery_app.autodiscover_tasks(['celery_tasks.sms'])


# 开启celery的worker
# celery -A celery实例应用包路径 worker -l info
# celery -A celery_tasks.main worker -l info