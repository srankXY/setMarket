# -*- utf-8 -*-

# config 类
class config(object):
    """
    外部配置，注：这样操作仅为方便改动，少调整代码
    """
    CONFIG = {
        # 代理
        'proxy': {
                'https': 'http://127.0.0.1:7890'
        },

        # redis
        'redisHost': '172.31.1.1',
        'redisPort': 6379,
        'redisDB': 0,
        'redisPassword': 'foobared',
    }
