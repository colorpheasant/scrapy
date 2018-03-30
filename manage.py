# -*-coding=utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """工程配置信息"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI ='mysql://root:mysql@127.0.0.1:3306/ihome_07'
    SQLALCHEMY_TRACK_MODIFICATIONS =False

app =Flask(__name__)
app.config.from_object(Config)
#創建連接到mysql数据哭的对象
db = SQLAlchemy(app)
@app.route('/index')
def index():
    return 'index'

if __name__ == '__main__':
    app.run(debug=True)