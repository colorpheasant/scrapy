# -*- coding:utf-8 -*-
# 实现注册和登录


from . import api
from flask import request,jsonify, current_app, session
import json
from iHome.utils.response_code import RET
from iHome import redis_store, db
from iHome.models import User
import re
from iHome.utils.common import login_required


@api.route('/sessions')
def check_login():
    """判断用户是否登录
    0.提示:该接口是用于前端在渲染界面时判断使用的根据不同的登录状态，展示不同的界面
    """

    user_id = session.get('user_id')
    name = session.get('name')

    return jsonify(errno=RET.OK, errmsg='OK', data={'user_id':user_id, 'name':name})


@api.route('/sessions', methods=['DELETE'])
@login_required
def logout():
    """提供退出登录"""

    # 1.清理session数据
    session.pop('user_id')
    session.pop('name')
    session.pop('mobile')

    return jsonify(errno=RET.OK, errmsg='退出登录成功')


@api.route('/sessions', methods=['POST'])
def login():
    """实现登录
    1.接受请求参数：手机号，明文密码
    2.判断是否缺少参数，并做手机号格式校验
    3.使用手机号查询该要登录的用户数据是否存在
    4.对密码进行校验
    5.将用户的状态保持信息写入到session
    6.响应登录结果
    """

    # 1.接受请求参数：手机号，明文密码
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')

    # 2.判断是否缺少参数，并做手机号格式校验
    if not all([mobile, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 做手机号格式校验
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.使用手机号查询该要登录的用户数据是否存在
    try:
        user = User.query.filter(User.mobile == mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.USERERR, errmsg='用户名或密码错误')

    # 4.对密码进行校验
    if not user.check_password(password):
        return jsonify(errno=RET.PWDERR, errmsg='用户名或密码错误')

    # 5.将用户的状态保持信息写入到session
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 6.响应登录结果
    return jsonify(errno=RET.OK, errmsg='登录成功')


@api.route('/users', methods=['POST'])
def register():
    """实现注册
    1.获取请求参数：手机号，短信验证码，密码
    2.判断参数是否缺少
    3.获取服务器的短信验证码
    4.并与客户端传入的验证码比较,如果一致
    5.创建User模型类对象
    6.保存注册数据到数据库
    7.响应结果
    """

    # 1.获取请求参数：手机号，短信验证码，密码
    # json_str = request.data
    # json_dict = json.loads(json_str)
    # json_dict = request.get_json()
    json_dict = request.json

    mobile = json_dict.get('mobile')
    sms_code_clinet = json_dict.get('sms_code')
    password = json_dict.get('password')

    # 2.判断参数是否缺少
    if not all([mobile, sms_code_clinet, password]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.获取服务器的短信验证码
    try:
        sms_code_server = redis_store.get('Mobile:' + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询短信验证码失败')
    # 判断数据是否为空
    if not sms_code_server:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码不存在')

    # 4.并与客户端传入的验证码比较,如果一致
    if sms_code_server != sms_code_clinet:
        return jsonify(errno=RET.DATAERR, errmsg='输入验证码有误')

    # 判断该用户是否已经注册
    if User.query.filter(User.mobile == mobile).first():
        return jsonify(errno=RET.DATAEXIST, errmsg='用户已注册')

    # 5.创建User模型类对象
    user = User()
    # 注册时，默认手机号就是用户名，如果后面需要更换用户名，也是提供的有接口和界面
    user.name = mobile
    user.mobile = mobile
    # 密码需要加密后才能存储
    # user.password_hash = '加密后的密码'
    user.password = password

    # 6.保存注册数据到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存注册数据失败')

    # 实现注册成功即登录：记住状态保持信息即可
    session['user_id'] = user.id
    session['name'] = user.name
    session['mobile'] = user.mobile

    # 7.响应结果
    return jsonify(errno=RET.OK, errmsg='注册成功')

