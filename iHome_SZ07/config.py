# -*- coding:utf-8 -*-


import redis
import logging


class Config(object):
    """加载配置"""

    # 开启调试模式
    DEBUG = True

    # 秘钥
    SECRET_KEY = 'AK0j4NSomJQKm8gD/917OniOIC8DEMQRP+xPBvGanEBieaADMBTA0EBTrJdAiXgU'

    # 配置mysql数据库:开发中使用真实IP
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_07'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis数据库：开发中使用真实IP
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379

    # 配置session数据存储到redis数据库
    SESSION_TYPE = 'redis'
    # 指定存储session数据的redis的位置
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 开启session数据的签名，意思是让session数据不以明文形式存储
    SESSION_USE_SIGNER = True
    # 設置session的会话的超时时长 ：一天
    PERMANENT_SESSION_LIFETIME = 3600 * 24


class DevelopmentConfig(Config):
    """创建调试环境下的配置类"""
    # 我们的爱家租房的房型，调试模式的配置和Config一致，所以pass

    # 如果是开发环境，日志等级就是DEBUG
    LOGGIONG_LEVEL = logging.DEBUG


class ProductionConfig(Config):
    """创建线上环境下的配置类"""

    # 重写有差异性的配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@192.168.72.77:3306/iHome'

    # 如果是生产环境，日志等级就是WARN
    LOGGIONG_LEVEL = logging.WARN


class UnittestConfig(Config):
    """单元测试的配置"""

    # 重写有差异性的配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/iHome_testcast_07'



# 准备工厂设计模式的原材料
configs =  {
    'default_config':Config,
    'development':DevelopmentConfig,
    'production':ProductionConfig,
    'unittest':UnittestConfig
}