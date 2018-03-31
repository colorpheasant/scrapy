# -*-coding=utf-8 -*-

from flask_script import  Manager
from flask_migrate import Migrate,MigrateCommand
from iHome import app,db
import os,base64

manager = Manager(app)

Migrate(app,db)
manager.add_command('db',MigrateCommand)


@app.route('/index',methods=['GET','POST'])
def index():
    #测试redis数据哭
    # redis_store.set('name','sz007')
    # #测试session:flask自带的session模块,用于存储session
    # from flask import session
    # session['name'] = 'sz07sz07'
    return 'index'

if __name__ == '__main__':
    # app.run(debug=True)
    manager.run()