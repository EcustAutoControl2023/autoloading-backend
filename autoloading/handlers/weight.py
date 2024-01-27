from autoloading.models.sensor import Traffic
from sqlalchemy.sql.expression import and_
import logging
from datetime import datetime

# 预估重量
def weight_estimate(goods_type,loader_id,time_difference): 
    current_load_weight = 0.0
    per_second_weight = 0
    #筛选数据
    filtered_traffic = Traffic.query.filter(and_(Traffic.loaderid==loader_id,Traffic.goodstype==goods_type)).all()
    
    filtered_data_length = len(filtered_traffic)
    #logging.debug(f'filtered_data_length{filtered_data_length}')
      
    #提取筛选后数据的某一属性
    start_load_times = [datetime.strptime(traffic.loadtime1, '%Y-%m-%d %H:%M:%S') for traffic in filtered_traffic]  
    stop_load_times = [datetime.strptime(traffic.loadtime2, '%Y-%m-%d %H:%M:%S') for traffic in filtered_traffic]  

    loader_task = [traffic.loadcurrent for traffic in filtered_traffic]

    #计算装载时间
    load_time = [(stop - start).total_seconds() for start, stop in zip(start_load_times, stop_load_times)]

    for i in range(filtered_data_length): 
        try:
            per_second_weight += loader_task[i] / load_time[i] * 1.0
        except ZeroDivisionError:
            print('error')
            return None
      
    per_second_weight /= filtered_data_length
    current_load_weight = per_second_weight * time_difference
    
    return current_load_weight
