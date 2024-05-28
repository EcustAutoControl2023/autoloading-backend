from autoloading.config import create_logger

def weight_estimate():
    wlogging = create_logger("weight")
        
    global per_second_weight

    goods_type = [
        "玉米", "黄豆", "大麦",
    ]
    weight_array = [0 for _ in range(len(goods_type))] 

    per_second_weight = dict(zip(goods_type, weight_array))  #键为商品种类，值为每秒装载重量

    
    for j in range(len(goods_type)):
        #筛选数据, 注意需要去除当前正在装车的数据
        filtered_traffic = Traffic.query.filter(Traffic.goodstype==goods_type[j]).limit(10)[:-1]
        # self.logging.debug(f'filtered_traffic: {filtered_traffic}')
        # 没有数据直接退出

        #提取筛选后数据的某一属性

        loader_weight_in = [traffic.truckweightin for traffic in filtered_traffic if traffic.truckweightin is not None]  # 车辆进场重量
        loader_weight_out = [traffic.truckweightout for traffic in filtered_traffic if traffic.truckweightout is not None]  # 车辆出场重量

        loader_weight_total = [(weight_out - weight_in) for weight_in, weight_out in zip(loader_weight_in, loader_weight_out)]  # 车辆装载净重
        # self.logging.debug(f'loader_weight_total: {loader_weight_total}')

        #计算装载时间
        load_time = [traffic.loadtimetotal for traffic in filtered_traffic if traffic.loadtimetotal is not None]  # 每一次任务的总装载时间
        # self.logging.debug(f'load_time: {load_time}')

        filtered_data_length = min(len(load_time),len(loader_weight_total))
        # self.logging.debug(f'filtered_data_length: {filtered_data_length}')

        if filtered_data_length == 0:
            return None

        sum_weight_per_second = 0
        for k in range(filtered_data_length):
            try:
                # print(f'\033[31mloadtime: {load_time[k]}\033[0m')
                # print(f'\033[31mloadtask: {loader_task[k]}\033[0m')
                sum_weight_per_second += loader_weight_total[k] / load_time[k] * 1.0
            except ZeroDivisionError:
                print('\033[31merror\033[0m')
                wlogging.debug('\033[31merror\033[0m')
                return None

            per_second_weight[goods_type[j]] = sum_weight_per_second / filtered_data_length

    print(per_second_weight)
    wlogging.debug(per_second_weight)