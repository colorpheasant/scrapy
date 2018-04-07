# -*- coding:utf-8 -*-


import redis
from flask import Flask
# session在flask中的扩展包
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from config import configs
from iHome.utils.common import RegexConverter
import logging
from logging.handlers import RotatingFileHandler


# 创建可以被外界导入的数据库连接对象
db = SQLAlchemy()
# 创建可以被外界导入的连接到redis数据库的对象
redis_store = None


# 在业务逻辑一开始就开启日志
def setupLogging(level):
    """
    如果是开发模式，'development' -> 'DEBUG'
    如果是生产模式， 'production' -> 'WARN'
    """
    # 设置日志的记录等级
    logging.basicConfig(level=level)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


# default_config == config_name
def get_app(config_name):
    """工厂方法：根据不同的配置信息，实例化出不同的app"""

    # 调用封装的日志
    setupLogging(configs[config_name].LOGGIONG_LEVEL)

    app = Flask(__name__)

    # 加载配置
    app.config.from_object(configs[config_name])

    # 创建连接到mysql数据库的对象
    # db = SQLAlchemy(app)
    db.init_app(app)

    # 创建连接到redis数据库的对象
    global redis_store
    redis_store = redis.StrictRedis(host=configs[config_name].REDIS_HOST, port=configs[config_name].REDIS_PORT)

    # 开启CSRF保护
    CSRFProtect(app)

    # 使用session在flask扩展实现将session数据存储在redis
    Session(app)

    # 需要现有路由转换器，后面html_blue中才可以直接匹配
    app.url_map.converters['re'] = RegexConverter

    # 注册蓝图：为了解决导入api时，还没有redis_store，造成的ImportError: cannot import name redis_store
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    # 注册静态html文件加载时的蓝图
    from iHome.web_html import html_blue
    app.register_blueprint(html_blue)

    return app
