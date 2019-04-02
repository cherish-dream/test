from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings


class FastDFSStorage(Storage):
    """自定义文件存储系统：
    将运营上传到django的文件转存到FastDFS服务器中的storage
    """

    def __init__(self, client_conf=None, base_url=None):
        """重写构造方法
        当django收到上传请求需要存储文件时，自动回调用构造方法，"但是不会传参数"
        """
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL


    def _open(name, mode='rb'):
        """存储系统、django打开文件时自动调用的
        必须重写
        因为这里是做文件上传，不会涉及到文件的打开，所以重写完直接pass
        """
        pass

    def _save(self, name, content):
        """
        要存储文件时自动调用的
        :param name: 要存储的文件的名字
        :param content: 要存储的文件的内容File类型的对象，需要调用read()方法，读取文件的二进制信息
        :return: file_id
        """
        # 创建fdfs客户端 'meiduo_mall/utils/fastdfs/client.conf'
        client = Fdfs_client(self.client_conf)
        # 调用上传的方法
        ret = client.upload_by_buffer(content.read())
        # 判断上传是否成功
        if ret.get('Status') != 'Upload successed.':
            raise Exception('upload file failed')
        # 如果上传成功
        file_id = ret.get('Remote file_id')
        return file_id

    def exists(self, name):
        """
        判断文件是否已经在存储系统中：
        True : 代表文件已经存在，django不会调用文件存储的方法
        False:代表文件不在本地文件存储系统中，告诉django该文件是新的文件，django会自动调用文件存储的方法
        :param name: 要判断是否存在的文件的名字
        :return: False（告诉django该文件是新的文件，django会自动调用文件存储的方法）
        """
        return False

    def url(self, name):
        """
        给外界模型类的中的ImageField字段调用的
        作用：是为了获取那张图片的全路径的
        :param name: 要获取全路径地址的文件的名字 
        :return: http://192.168.103.132:8888/group1/M00/00/02/wKhnhFsx-QaAIEByAAC4j90Tziw40.jpeg
        """
        # 'http://192.168.103.132:8888/'
        return self.base_url + name




