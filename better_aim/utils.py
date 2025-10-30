import hashlib
import random
import string


def generate_random_string():
    """生成随机的20位字符串"""
    characters = string.ascii_letters + string.digits  # 包含字母和数字
    return ''.join(random.choice(characters) for _ in range(20))