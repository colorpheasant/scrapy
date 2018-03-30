# -*-coding=utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CsrfProtect
import os,base64
class Config(object):
    """工程配置信息"""
    DEBUG = True
    # SECRET_KEY = '12345UHSDIFHIO@123'
    SQLALCHEMY_DATABASE_URI ='mysql://root:mysql@127.0.0.1:3306/ihome_07'
    SQLALCHEMY_TRACK_MODIFICATIONS =False
    #配置redis数据:
    REDIS_HOST='127.0.0.1'
    REDIS_PORT=6379

app =Flask(__name__)
app.config.from_object(Config)
#創建連接到mysql数据哭的对象
db = SQLAlchemy(app)

redis_store =redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

CsrfProtect(app)
@app.route('/index',methods=['GET','POST'])
def index():
    #测试redis数据哭
    redis_store.set('name','sz007')
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)