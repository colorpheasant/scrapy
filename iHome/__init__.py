# -*-coding=utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
#session在扩展的包
from flask_session import Session
from config import Config
app =Flask(__name__)
app.config.from_object(Config)
#創建連接到mysql数据哭的对象
db = SQLAlchemy(app)

redis_store =redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CSRFProtect(app)

#使用session在flask中的扩展讲session存储在redis
Session(app)