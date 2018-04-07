# -*- coding:utf-8 -*-
# 提供个人中心数据


from . import api
from flask import session, current_app, jsonify, request, g
from iHome.models import User
from iHome.utils.response_code import RET
from iHome.utils.image_storage import upload_image
from iHome import db, constants
from iHome.utils.common import login_required


@api.route('/users/auth', methods=['GET'])
@login_required
def get_user_auth():
    """查询实名认证信息
    0.判断用户是否登录
    1.获取user_id,查询user信息
    2.构造响应数据
    3.响应结果
    """

    # 1.获取user_id,查询user信息
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 2.构造响应数据
    response_data = user.auth_to_dict()

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', data=response_data)


@api.route('/users/auth', methods=['POST'])
@login_required
def set_user_auth():
    """提供用户实名认证
    0.判断用户是否是登录用户 @login_required
    1.接受参数：real_name , id_card
    2.判断参数是否缺少：这里就不对身份证进行格式的校验，省略掉
    3.查询当前的登录用户模型对象
    4.将real_name , id_card赋值给用户模型对象
    5.将新的数据写入到数据库
    6.响应结果
    """

    # 1.接受参数：real_name , id_card
    json_dict = request.json
    real_name = json_dict.get('real_name')
    id_card = json_dict.get('id_card')

    # 2.判断参数是否缺少：这里就不对身份证进行格式的校验，省略掉
    if not all([real_name, id_card]):
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.查询当前的登录用户模型对象
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 4.将real_name , id_card赋值给用户模型对象
    user.real_name = real_name
    user.id_card = id_card

    # 5.将新的数据写入到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='保存实名认证数据失败')

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='实名认证成功')


@api.route('/users/name', methods=['PUT'])
@login_required
def set_user_name():
    """修改用户名
    0.先判断用户是否登录 @login_required
    1.接受用户传入的新名字， new_name
    2.判断参数是否为空
    3.查询当前登录用户
    4.将new_name赋值给当前的登录用户的name属性
    5.将新的数据写入到数据库
    6.响应结果
    """

    # 1.接受用户传入的新名字， new_name
    json_dict = request.json
    new_name = json_dict.get('name')

    # 2.判断参数是否为空
    if not new_name:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少参数')

    # 3.查询当前登录用户
    # user_id = session.get('user_id')
    user_id = g.user_id
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 4.将new_name赋值给当前的登录用户的name属性
    user.name = new_name

    # 5.将新的数据写入到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储用户名失败')

    # 修改用户名时，好需要修改session里面的name
    session['name'] = new_name

    # 6.响应结果
    return jsonify(errno=RET.OK, errmsg='修改用户名成功')



@api.route('/users/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """提供用户头像上传
    0.先判断用户是否登录 @login_required
    1.接受请求参数:avatar对应的图片数据，并校验
    2.调用上传图片的工具方法
    3.存储图片的key到user.avatar_url属性中
    4.响应上传结果，在结果中传入avatar_url，方便用户上传完成后立即刷新头像
    """

    # 1.接受请求参数:avatar对应的图片数据，并校验
    try:
        image_data = request.files.get('avatar')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='头像参数错误')

    # 2.调用上传图片的工具方法
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传头像失败')

    # 3.存储图片的key到user.avatar_url属性中
    # 获取登录用户的user_id
    # user_id = session.get('user_id')
    user_id = g.user_id

    # 查询登录用户对象
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')
    # 给登录用户模型属性赋新值
    user.avatar_url = key
    # 将新值保存的数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储用户头像地址失败')

    # 4.响应上传结果，在结果中传入avatar_url，方便用户上传完成后立即刷新头像
    # 拼接访问头像的全路径
    # http://oyucyko3w.bkt.clouddn.com/FtEAyyPRhUT8SU3f5DNPeejBjMV5
    avatar_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='上传头像成功', data=avatar_url)


@api.route('/users')
@login_required
def get_user_info():
    """提供用户个人信息
    0.先判断用户是否登录 @login_required
    1.获取用户id (user_id)
    2.查询该登录用户的user信息
    3.构造响应数据
    4.响应数据
    """

    # 1.获取用户id (user_id)
    # user_id = session.get('user_id')
    user_id = g.user_id

    # 2.查询该登录用户的user信息
    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')

    # 3.构造响应数据
    response_data = user.to_dict()

    # 4.响应数据
    return jsonify(errno=RET.OK, errmsg='OK', data=response_data)
