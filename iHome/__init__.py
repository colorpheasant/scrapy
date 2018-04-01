# -*-coding=utf-8 -*-

from werkzeug.routing import BaseConverter

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
#session在扩展的包
from flask_session import Session
# from config import Config,DevelopmentConfig,ProductionConfig
from config import configs
db = SQLAlchemy()
redis_store = None
def get_app(config_name):
    """工厂方法:根据不同配置信息,实例化不同的app"""
    app =Flask(__name__)

    app.config.from_object(configs[config_name])
    #創建連接到mysql数据哭的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    global redis_store
    redis_store =redis.StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)

    CSRFProtect(app)

    #使用session在flask中的扩展讲session存储在redis
    Session(app)

    return app