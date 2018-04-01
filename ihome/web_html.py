# -*-coding=utf-8 -*-

from flask import Blueprint,current_app
html_blue =Blueprint('html_blue',__name__)
@html_blue.route('/<re(".*"):file_name>')
def get_static_html(file_name):
    """获取静态文件"""
    if not file_name:
        file_name ='index.html'
    if file_name !='favicon.ico':
        file_name='html/'+file_name
    #使用file_path去查询制定路径下html
    return current_app.send_static_file(file_name)