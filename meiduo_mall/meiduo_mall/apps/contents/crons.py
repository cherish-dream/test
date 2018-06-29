from collections import OrderedDict
from django.conf import settings
from django.template import loader
import os
import time

from goods.models import GoodsChannel
from .models import ContentCategory


def generate_static_index_html():
    """
    生成静态的主页html文件
    """
    print('%s: generate_static_index_html' % time.ctime())
    # 商品频道及分类菜单
    # 使用有序字典保存类别的顺序
    # categories = {
    #     1: { # 组1
    #         'channels': [{'id':, 'name':, 'url':},{}, {}...],
    #         'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]
    #     },
    #     2: { # 组2
    #
    #     }
    # }

    # 有序字典
    categories = OrderedDict()
    # 把频道数据查询b并排序，一共是37条记录
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 遍历37条记录
    for channel in channels:
        # 取出每条记录的group_id
        group_id = channel.group_id  # 当前组


        if group_id not in categories:
            # 实现分组
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # cat1对应的是商品分类的一级分类（频道）
        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别 ： cat2 商品二级分类
        for cat2 in cat1.goodscategory_set.all():
            cat2.sub_cats = []
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)

    # 广告内容
    contents = {}
    content_categories = ContentCategory.objects.all()
    for cat in content_categories:
        contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

    # 渲染模板
    context = {
        'categories': categories,
        'contents': contents
    }

    # 目的：渲染模板：使用查询到的上下文，渲染出一个html文本字符串，该字符串将来需要存储到front_end_pc

    # 从项目的默认的template文件夹中，获取index.html，构造模板对象
    # get_template ：只会从项目的默认的模板文件夹中去读html模板，所以需要给该方法指定默认的模板文件
    template = loader.get_template('index.html')
    html_text = template.render(context)
    # 提示：templates中的index.html是临时的，不需要展示的，只为get_template而存在

    # 将html文本信息写入到前端的front_end_pc文件中，并命名为index.html
    file_path = os.path.join(settings.GENERATED_STATIC_HTML_FILES_DIR, 'index.html')
    # 第三个参数encoding ： wield辅助解决定时器crontab中文编码的问题
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)