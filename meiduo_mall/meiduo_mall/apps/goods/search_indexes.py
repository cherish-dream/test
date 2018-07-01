from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    # 符合字段：我们可以指定哪些索引字段集成到text内部中
    # search?name=iphone
    # 符合字段：search?text=iphone
    text = indexes.CharField(document=True, use_template=True)

    id = indexes.IntegerField(model_attr='id')
    # 以name作为索引，将来输入商品名字就可以搜索上平
    name = indexes.CharField(model_attr='name')
    # 注意点：indexes.字段的类型；该字段的类型需要跟模型类的属性的类型一致
    price = indexes.CharField(model_attr='price')
    default_image_url = indexes.CharField(model_attr='default_image_url')
    comments = indexes.IntegerField(model_attr='comments')

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)