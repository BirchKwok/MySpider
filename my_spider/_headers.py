from ._common_config import *


def get_random_headers():
    """获取随机请求头"""

    ua=UserAgent() 
    return {"User-Agent":ua.random} 
