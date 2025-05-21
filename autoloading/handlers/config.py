from flask import render_template, session
# import request
from flask import request
import logging

from autoloading.models.base import db
from autoloading.models.sensor import CoConfig, LoaderConfig
from autoloading.handlers.loaderpoint import LoadPoint

g_loader_id = '401A'
g_goods_type = '黄豆'

# 拿到所有的物料类型
def get_goods_type_list():
    return LoadPoint.GoodsTypeList

# 拿到料口和垛位的对应关系
def get_location_stackpos_dict():
    LocationStackPosList = list(zip(LoadPoint.StackposList, LoadPoint.LocationList))
    LocationStackPosDict = {k:v for k,v in LocationStackPosList}

    return LocationStackPosDict

def get_locationid_location_dict():
    LocationStackPosList = list(zip(LoadPoint.StackposList, LoadPoint.StackposList))
    LocationStackPosDict = {k:v for k,v in LocationStackPosList}
    for k,v in LocationStackPosDict.items():
        if 'A' in v:
            v = v.replace('A', '南')
        elif 'B' in v:
            v = v.replace('B', '北')

        LocationStackPosDict[k] = v

    return LocationStackPosDict

# 将配置保存到数据库
def save_config(loader_id, goods_type, duration, weight):
    loader_config = LoaderConfig.query.filter_by(loader_id=loader_id).all()
    logging.debug(f'len(loader_config): {len(loader_config)}')
    lsd = get_location_stackpos_dict()


    if len(loader_config) == 1:
        loader_config = loader_config[0]

        co_config = CoConfig.query.filter(CoConfig.loader_id==loader_config.id, CoConfig.goods_type==goods_type).all()
        logging.debug(f'len(co_config): {len(co_config)}')
        if len(co_config) == 1:
            loader_config.update_time = db.func.now()
            co_config = co_config[0]
            logging.debug(f'更新品种({goods_type})的配置！')
            co_config.duration = duration
            co_config.weight = weight
        elif len(co_config) == 0:
            logging.debug(f'增加品种({goods_type})的配置！')
            co_config = CoConfig(
                loader_id=loader_id,
                goods_type=goods_type,
                duration=duration,
                weight=weight,
            )
            loader_config.co_config.append(co_config)
        else:
            logging.debug(f'每个料口一个品种只有一个配置！')
    else:
        # create a new loader config
        loader_config= LoaderConfig(
            loader_id=loader_id,
            store_id=lsd[loader_id],
        )
        co_config = CoConfig(
            goods_type=goods_type,
            duration=duration,
            weight=weight,
        )
        loader_config.co_config = [co_config]
        logging.debug(f'Loader ID: {loader_id}')

    db.session.add(loader_config)
    db.session.add(co_config)
    db.session.commit()

    # db.session.add(loader_config)
    # db.session.commit()

# 从数据库中读取配置
def get_config(loader_id, goods_type):
    loader = LoaderConfig.query.filter_by(loader_id=loader_id).all()
    # TODO: 默认值的给定方法
    if len(loader) == 0:
        save_config(loader_id, goods_type, 600, 20)
    loader = LoaderConfig.query.filter_by(loader_id=loader_id).all()[-1]
    co_config = CoConfig.query.filter(CoConfig.loader_id==loader.id, CoConfig.goods_type==goods_type).all()

    if len(co_config) > 0:
        return {
            'duration': co_config[0].duration,
            'weight': co_config[0].weight,
        }
    else:
        return {
            'duration': 600,
            'weight': 20,
        }


def config():
    global g_loader_id
    global g_goods_type

    # if post request is made
    if request.method == 'POST':
        # get the form data
        loader_id = request.form.get('loader_id')
        duration = request.form.get('duration')
        weight = request.form.get('weight')
        goods_type = request.form.get('goods_type')

        g_loader_id = loader_id
        g_goods_type = goods_type

        logging.debug(f'Loader ID: {loader_id}')
        logging.debug(f'Duration: {duration}')
        logging.debug(f'Weight: {weight}')
        logging.debug(f'Goods Type: {goods_type}')
        save_config(loader_id, goods_type, duration, weight)



    return render_template('config.html', configs=get_config(g_loader_id, g_goods_type), goods_type_list=get_goods_type_list(), lld=get_locationid_location_dict(), select={
        'loader_id': g_loader_id,
        'goods_type': g_goods_type,
    })



