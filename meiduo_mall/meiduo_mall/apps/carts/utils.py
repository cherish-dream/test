import pickle
import base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    合并cookie中的购物车到redis
    :param request: 本次登录请求
    :param response: 本次登录响应
    :param user: 本次登录的用户
    :return: cookie
    """

    # 获取cookie中的购物车数据
    cart_str = request.COOKIES.get('cart')

    # 如果cookie中没有购物车数据的，直接返回响应
    if not cart_str:
        return response

    # 将购物车字符串数据转成字典
    cookie_cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))

    # 获取redis中的购物车数据
    redis_conn = get_redis_connection('carts')
    redis_cart_dict = redis_conn.hgetall('cart_%s' % user.id)
    redis_cart_selected = redis_conn.smembers('selected_%s' % user.id)

    # 将redis中的字节类型的sku_id和count转成int,跟cart_dict匹配
    # {
    #     b'sku_id':b'count',
    #     b'sku_id': b'count'
    # }
    new_redis_cart_dict = {}
    for sku_id, count in redis_cart_dict.items():
        # 存储redis中原有的那部分购物车数据
        new_redis_cart_dict[int(sku_id)] = int(count)

    # 遍历cookie_cart_dict，取出数据合并到new_redis_cart_dict
    # {
    #     sku_id10: {
    #         "count": 10, // 数量
    #         "selected": True // 是否勾选
    #     },
    #     sku_id20: {
    #         "count": 20,
    #         "selected": False
    #     },
    #     ...
    # }

    # new_redis_cart_selected = []
    for sku_id, cookie_dict in cookie_cart_dict.items():
        # 保存cookie中的购物车数据到redis: 并使用cookie中的count覆盖redis中的count
        new_redis_cart_dict[sku_id] = cookie_dict['count']

        if cookie_dict['selected']:
            redis_cart_selected.add(sku_id)

    # 将cookie中的购物车数据合并到redis中
    pl = redis_conn.pipeline()
    pl.hmset('cart_%s' % user.id, new_redis_cart_dict)
    pl.sadd('selected_%s' % user.id, *redis_cart_selected)
    pl.execute()

    # 清空cookie中的购物车数据
    response.delete_cookie('cart')

    return response