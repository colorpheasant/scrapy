# -*- coding:utf-8 -*-
# 图片验证码和短信验证码


from . import api
from iHome.utils.captcha.captcha import captcha
from flask import request, make_response, jsonify, abort, current_app
from iHome import redis_store
from iHome import constants
from iHome.utils.response_code import RET
import logging
import json
import re
import random
from iHome.utils.sms import CCP


@api.route('/sms_code', methods=['POST'])
def send_sms_code():
    """发送短信验证码
    1.接受参数：手机号，图片验证码，uuid
    2.判断参数是否缺少，并且要对手机号进行校验
    3.获取服务器存储的图片验证码，uuid作为key
    4.与客户端传入的图片验证码对比，如果对比成功
    5.生成短信验证码
    6.使用云通讯将短信验证码发送到注册用户手中
    7.存储短信验证码到redis中
    8.响应短信发送的结果
    """

    # 1.接受参数：手机号，图片验证码，uuid
    # data : 保存请求报文里面的原始的字符串，开发文档约定，客户端发送的是json字符串
    json_str = request.data
    json_dict = json.loads(json_str)

    mobile = json_dict.get('mobile')
    imageCode_client = json_dict.get('imagecode')
    uuid = json_dict.get('uuid')

    # 2.判断参数是否缺少，并且要对手机号进行校验
    if not all([mobile, imageCode_client, uuid]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')
    # 校验手机号码是否合法
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg='手机号码格式错误')

    # 3.获取服务器存储的图片验证码，uuid作为key
    try:
        imageCode_server = redis_store.get('ImageCode:' + uuid)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询服务器验证码失败')

    # 判断是否为空或者过期
    if not imageCode_server:
        return jsonify(errno=RET.NODATA, errmsg='验证码不存在')

    # 4.与客户端传入的图片验证码对比，如果对比成功
    if imageCode_server.lower() != imageCode_client.lower():
        return jsonify(errno=RET.DATAERR, errmsg='验证码输入有误')

    # 5.生成短信验证码
    sms_code = '%06d' % random.randint(0, 999999)
    current_app.logger.debug('短信验证码为：' + sms_code)

    # 6.使用云通讯将短信验证码发送到注册用户手中
    # 注释以下代码，是在我们验证逻辑通过的前提下，为了方便不在频繁的发送短信验证码，我就使用假的手机号绑定我们自己生产的验证码
    # result = CCP().send_template_sms(mobile, [sms_code , constants.SMS_CODE_REDIS_EXPIRES/60], '1')
    # if result != 1:
    #     return jsonify(errno=RET.THIRDERR, errmsg='发送短信验证码失败')

    # 7.存储短信验证码到redis中:短信验证码在redis中的有效期一定要和短信验证码的提示信息一致
    try:
        redis_store.set('Mobile:' + mobile, sms_code, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='存储短信验证码失败')

    # 8.响应短信发送的结果
    return jsonify(errno=RET.OK, errmsg='发送短信验证码成功')


@api.route('/image_code')
def get_image_code():
    """提供图片验证码
    1.接受请求，获取uuid
    2.生成图片验证码
    3.使用UUID存储图片验证码内容到redis
    4.返回图片验证码
    """

    # 1.接受请求，获取uuid
    uuid = request.args.get('uuid')
    last_uuid = request.args.get('last_uuid')
    if not uuid:
        abort(403)
        # return jsonify(errno=RET.PARAMERR, errmsg=u'缺少参数')

    # 2.生成验证码:text是验证码的文字信息，image验证码的图片信息
    name, text, image = captcha.generate_captcha()
    print text
    # 将调试信息写入到?logs/log
    # logging.debug('图片验证码文字信息：' + text)
    current_app.logger.debug('图片验证码文字信息：' + text)

    # 3.使用UUID存储图片验证码内容到redis
    try:
        if last_uuid:
            # 上次的uuid还存在，删除上次的uuid对应的记录
            redis_store.delete('ImageCode:' + last_uuid)

        # 保存本次需要记录的验证码数据
        redis_store.set('ImageCode:' + uuid, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        print e
        # 将错误信息写入到?logs/log
        # logging.error(e)
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg=u'保存验证码失败')

    # 4.返回图片验证码
    resposne = make_response(image)
    resposne.headers['Content-Type'] = 'image/jpg'
    return resposne