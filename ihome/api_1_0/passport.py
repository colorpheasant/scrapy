# -*-coding=utf-8 -*-
#实现注册和登陆
from . import api
from flask import request,jsonify,current_app
import json
from ihome.utils.response_code import  RET
from ihome import redis_store,db
from ihome.models import User
@api.route('/users',methods=['POST'])
def register():
    """实现注册"""
    # json_str = request.data
    # json_dict =json.loads(json_str)
    # json_dict = request.get_json()
    json_dict =request.json
    mobile =json_dict.get('mobile')
    smc_code_client =json_dict.get('sms_code')
    password =json_dict.get('password')

    if not all(mobile,smc_code_client,password):
        return jsonify(errno=RET.PARAMERR,errmsg="缺少参数")
    try:
        sms_code_server =redis_store.get('Mobile:'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno =RET.PARAMERR,errmsg='查询短信验证码失败')
    if not sms_code_server:
        return jsonify(errno =RET.NODATA,errmsg ='短信验证码不存在')
    if sms_code_server != smc_code_client:
        return jsonify(errno =RET.DATAERR,errmsg='输入验证码有误')
    user =User()
    user.name = mobile
    user.mobile = mobile
    user.password_hash =password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno =RET.DBERR,errmsg='保存注册数据失败')

    return jsonify(errno=RET.OK,errmsg='注册成功')