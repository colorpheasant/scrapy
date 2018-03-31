# -*-coding=utf-8 -*-
import redis
class Config(object):
    """工程配置信息"""
    DEBUG = True
    SECRET_KEY = '12345UHSDIFHIO@123'
    SQLALCHEMY_DATABASE_URI ='mysql://root:mysql@127.0.0.1:3306/ihome_07'
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    #配置redis数据:
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379
    #配置session数据存储到redis
    SESSION_TYPE ='redis'
    SESSION_REDIS =redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SIGNER = True
    PERMANENT_SESSION_LIFETIME =3600*24