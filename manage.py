# -*-coding=utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_script import  Manager
from flask_migrate import Migrate,MigrateCommand
#session在扩展的包
from flask_session import Session
import os,base64
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
app =Flask(__name__)
app.config.from_object(Config)
#創建連接到mysql数据哭的对象
db = SQLAlchemy(app)



redis_store =redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CSRFProtect(app)
manager = Manager(app)

Migrate(app,db)
manager.add_command('db',MigrateCommand)

#使用session在flask中的扩展讲session存储在redis
Session(app)

@app.route('/index',methods=['GET','POST'])
def index():
    #测试redis数据哭
    redis_store.set('name','sz007')
    #测试session:flask自带的session模块,用于存储session
    from flask import session
    session['name'] = 'sz07sz07'
    return 'index'

if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()