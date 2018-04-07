# -*- coding:utf-8 -*-
# 实现房屋模块接口


from . import api
from iHome.models import Area, House, Facility, HouseImage, Order
from flask import current_app, jsonify, request, g, session
from iHome.utils.response_code import RET
from iHome.utils.common import login_required
from iHome import db, constants, redis_store
from iHome.utils.image_storage import upload_image
import datetime


# http://127.0.0.1:5000/search.html?aid=2&aname=&sd=&ed=&p=
@api.route('/houses/search')
def get_houses_search():
    """搜索房屋列表
    1.查询所有的房屋信息
    2.构造响应数据
    3.响应结果
    """

    current_app.logger.debug(request.args)

    # 获取地区参数
    aid = request.args.get('aid')
    # 获取排序参数: new:最新，按照发布时间倒序; booking:订单量，安装订单量倒序；price-inc 价格低到高；price-des 价格高到低
    sk = request.args.get('sk')
    # 获取用户传入的页码
    p = request.args.get('p', '1') # 如果不传，默认第一页
    # 获取入住时间
    sd = request.args.get('sd', '') # u'2018-04-07'
    # 获取离开时间
    ed = request.args.get('ed', '') # u'2018-04-08'

    start_date = None
    end_date = None

    # 校验参数
    try:
        p = int(p)

        if sd:
            # 将时间字符串转成时间对象
            start_date = datetime.datetime.strptime(sd, '%Y-%m-%d')
        if ed:
            # 将时间字符串转成时间对象
            end_date = datetime.datetime.strptime(ed, '%Y-%m-%d')
        # 自己校验入住时间是否小于离开的时间
        if start_date and end_date:
            # 断言：入住时间一定小于离开时间，如果不满足，就抛出异常
            assert start_date < end_date, Exception('入住时间有误')

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数有误')

    # 在查询数据之前，读取缓存数据
    try:
        name = 'house_list_%s_%s_%s_%s' % (aid, sd, ed, sk)
        response_data = redis_store.hget(name, p)
        return jsonify(errno=RET.OK, errmsg='OK', data=eval(response_data))
    except Exception as e:
        current_app.logger.error(e)

    # 1.查询所有的房屋信息 houses == [House,House,House,...]
    try:
        # 无条件查询所有房屋数据
        # houses = House.query.all()

        # 得到BaseQuery对象，保存即将要查询出来的数据
        house_query = House.query

        # 根据用户选中的城区信息，筛选出满足条件的房屋信息
        if aid:
            house_query = house_query.filter(House.area_id == aid)

        # 根据用户传入的入住时间和离开的时间，跟订单里面的时间进行对比
        # 如果用户传入的时间段，在订单中，也存在，就把满足冲突条件的订单查询出来 conflict_orders
        conflict_orders = []
        if start_date and end_date:
            conflict_orders = Order.query.filter(end_date > Order.begin_date, start_date < Order.end_date).all()
        elif start_date:
            conflict_orders = Order.query.filter(start_date < Order.end_date).all()
        elif end_date:
            conflict_orders = Order.query.filter(end_date > Order.begin_date).all()

        # 再通过冲突的订单，查询出里面的house_id,封装到列表中 conflict_house_ids
        if conflict_orders:
            conflict_house_ids = [order.house_id for order in conflict_orders]
            # 最后在查询House是，not_in(conflict_house_ids)
            house_query = house_query.filter(House.id.notin_(conflict_house_ids))


        # 根据排序规则对数据进行排序
        if sk == 'booking':
            house_query = house_query.order_by(House.order_count.desc())
        elif sk == 'price-inc':
            house_query = house_query.order_by(House.price.asc())
        elif sk == 'price-des':
            house_query = house_query.order_by(House.price.desc())
        else:
            house_query = house_query.order_by(House.create_time.desc())

        # 无条件的从BaseQuery对象中取出数据
        # houses = house_query.all()

        # 需要使用分页功能，避免一次性查询所有数据，使用分页代码，替换all()
        # 每页两条数据 paginate == 一本书，书里面有好多页
        paginate = house_query.paginate(p, constants.HOUSE_LIST_PAGE_CAPACITY, False)
        # 获取当前页的房屋模型对象 houses == [House, House],
        houses = paginate.items
        # 获取一共分了多少页，一定要传给前端
        total_page = paginate.pages

    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋信息失败')

    # 2.构造响应数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    # 提示：如果重新构造了响应数据，需要把之前前端界面的house_dict_list的获取修改一下response.data.houses
    response_data = {
        'houses':house_dict_list,
        'total_page':total_page
    }

    # 缓存房屋列表数据
    try:
        name = 'house_list_%s_%s_%s_%s' % (aid,sd,ed,sk)

        # 创建redis管道:用于存放后面的所有的redis操作的，看做一整整体
        pipeline = redis_store.pipeline()
        # 开启事务
        pipeline.multi()

        # 需要看做整体的redis操作
        redis_store.hset(name, p, response_data)
        redis_store.expire(name, constants.HOUSE_LIST_REDIS_EXPIRES)

        # 执行/提交事务
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)
        # redis发现异常，不需要手动回滚

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', data=response_data)


@api.route('/houses/index')
def get_house_index():
    """提供房屋最新的推荐
    1.查询最新发布的五个房屋信息,（按照时间排倒序）
    2.构造响应数据
    3.响应结果
    """

    # 1.查询最新发布的五个房屋信息 houses == [House, House, House, ...]
    try:
        houses = House.query.order_by(House.create_time.desc()).limit(constants.HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')

    # 2.构造响应数据
    house_dict_list = []
    for house in houses:
        house_dict_list.append(house.to_basic_dict())

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', data=house_dict_list)


@api.route('/houses/detail/<int:house_id>')
def get_house_detail(house_id):
    """提供房屋详情
    0.获取house_id，通过正则。如果house_id不满足条件不会进入到使用当中
    1.查询房屋全部信息
    2.构造响应数据
    3.响应结果
    """

    # 1.查询房屋全部信息
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 2.构造响应数据
    response_data = house.to_full_dict()

    # 获取user_id : 当用户登录后访问detail.html，就会有user_id，反之，没有user_id
    login_user_id = session.get('user_id', -1)

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', data={'house':response_data, 'login_user_id':login_user_id})


@api.route('/houses/image', methods=['POST'])
@login_required
def upload_house_imaeg():
    """发布房屋图片
    0.判断用户是否是登录 @login_required
    1.接受参数：image_data, house_id， 并做校验
    2.使用house_id查询house模型对象数据，因为如果查询不出来，就不需要上传图片了
    3.调用上传图片的工具方法，发布房屋图片
    4.将图片的七牛云的key,存储到数据库
    5.响应结果：上传的房屋图片，需要立即刷新出来
    """

    # 1.接受参数：image_data, house_id， 并做校验
    try:
        image_data = request.files.get('house_image')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='无法收到房屋图片')

    house_id = request.form.get('house_id')
    if not house_id:
        return jsonify(errno=RET.PARAMERR, errmsg='缺少必传参数')

    # 2.使用house_id查询house模型对象数据，因为如果查询不出来，就不需要上传图片了
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询房屋数据失败')
    if not house:
        return jsonify(errno=RET.NODATA, errmsg='房屋不存在')

    # 3.调用上传图片的工具方法，发布房屋图片
    try:
        key = upload_image(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='上传房屋图片失败')

    # 4.将图片的七牛云的key,存储到数据库
    house_image = HouseImage()
    house_image.house_id = house_id
    house_image.url = key

    # 选择一个图片，作为房屋的默认图片
    if not house.index_image_url:
        house.index_image_url = key

    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='存储房屋图片失败')

    # 5.响应结果：上传的房屋图片，需要立即刷新出来
    image_url = constants.QINIU_DOMIN_PREFIX + key
    return jsonify(errno=RET.OK, errmsg='发布房屋图片成功', data={'image_url':image_url})


# title为 1 的房屋是 樱木花道 发布的，他是房东

@api.route('/houses', methods=['POST'])
@login_required
def pub_house():
    """发布新房源
    0.判断用户是否登录 @login_required
    1.接受所有参数,并判断是否缺少
    2.校验参数：price / deposit， 需要用户传入数字
    3.实例化房屋模型对象，并给属性赋值
    4.保存到数据库
    5.响应结果
    """

    # 1.接受所有参数,并判断是否缺少
    json_dict = request.json

    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    if not all([title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数缺失')

    # 2.校验参数：price / deposit， 需要用户传入数字
    # 提示：在开发中，对于像价格这样的浮点数，不要直接保存浮点数，因为有精度的问题，一般以分为单位
    try:
        price = int(float(price) * 100) # 0.1元 ==> 10分
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='参数格式错误')

    # 3.实例化房屋模型对象，并给属性赋值
    house = House()
    house.user_id = g.user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 处理房屋的设施 facilities = [2,4,6]
    facilities = json_dict.get('facility')
    # 查询出被选中的设施模型对象
    house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    # 4.保存到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg='发布新房源失败')

    # 5.响应结果
    return jsonify(errno=RET.OK, errmsg='发布新房源成功', data={'house_id':house.id})


@api.route('/areas')
def get_areas():
    """提供城区信息
    1.查询所有的城区信息
    2.构造响应数据
    3.响应结果
    """

    # 查询缓存数据，如果有缓存数据，就使用缓存数据，反之，就查询，并缓存新查询的数据
    try:
        area_dict_list = redis_store.get('Areas')
        if area_dict_list:
            return jsonify(errno=RET.OK, errmsg='OK', data=eval(area_dict_list))
    except Exception as e:
        current_app.logger.error(e)

    # 1.查询所有的城区信息 areas == [Area,Area,Area,...]
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='查询城区信息失败')

    # 2.构造响应数据
    area_dict_list = []
    for area in areas:
        area_dict_list.append(area.to_dict())

    # 缓存城区信息到redis : 没有缓存成功也没有影响，因为前爱你会判断和查询
    try:
        redis_store.set('Areas', area_dict_list, constants.AREA_INFO_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    # 3.响应结果
    return jsonify(errno=RET.OK, errmsg='OK', data=area_dict_list)

