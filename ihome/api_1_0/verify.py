# -*-coding=utf-8 -*-
#图片的验证码和短信的验证码
from  . import  api
from ihome.utils.captcha.captcha import captcha
from flask import  request,make_response,jsonify,abort,current_app
from ihome import redis_store
from ihome import constants
from ihome.utils.response_code import RET
import logging
import json
import re
import random
from ihome.utils.sms import CCP
@api.route('/sms_code',methods=['POST'])
def send_sms_code():
    """发送短信验证码"""
    json_str = request.data
    json_dict =json.loads(json_str)

    mobile =json_dict.get('mobile')
    imageCode_client =json_dict.get('imagecode')
    uuid = json_dict.get('uuid')

    if not all([mobile,imageCode_client,uuid]):
        return jsonify(errno=RET.PARAMERR,errmsg="缺少参数")
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return jsonify(error=RET.PARAMERR,errmsg="手机号码格式错误")

    try:
        imageCode_server =redis_store.get('ImageCode:' + uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="验证嘛失败")

    if not imageCode_server:
        return jsonify(error=RET.PARAMERR,errmsg="验证码不存在")

    if imageCode_server.lower() != imageCode_client.lower():
        return jsonify(errno=RET.DATAERR,errmsg='验证码输入有误')

    sms_code = '%06d'% random.randint(0,999999)
    current_app.logger.debug('短信的验证码为:'+ sms_code)

    result=CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES/60],'1')
    if result !=1:
        return jsonify(errno=RET.THIRDERR,errmsg='发送短信验证码失败')
    try:
        redis_store.set('Mobile:'+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg='存储短信验证码失败')

    return jsonify(errno=RET.DBERR,errmsg='存储短信验证码失败')

@api.route('/image_code')
def get_image_code():

    uuid =request.args.get('uuid')
    last_uuid =request.args.get('last_uuid')
    if not uuid:
        abort(403)
    #生成验证码:text是验证码的文职信息
    name,text,image=captcha.generate_captcha()
    # logging.debug('验证码信息:'+text)
    current_app.logger.debug('验证码信息:'+text)
    try:
        if  last_uuid:
            redis_store.delete('ImageCode:'+last_uuid)
        redis_store.set('ImageCode:'+uuid,text,constants.IMAGE_CODE_REDIS_EXPIRES)

    except Exception as e:
        print e
        logging.error(e)
        current_app.logger.error(e)
        return jsonify(error=RET.DBERR,errmsg=u'保存验证码失败')
    response =make_response(image)
    response.headers['Content-Type']='image/jpg'
    return response