from autoloading.models.sensor import Traffic
import logging

# 预估重量
def weight_estimate(goods_type,loader_id,time_difference): 

    per_second_weight = 0
    #筛选数据
    filtered_traffic = Traffic.query.filter(and_(Traffic.loaderid==loader_id,Traffic.goodstype==goods_type)).all()
    
    filtered_data_length = len(filtered_traffic)
    logging.debug(f'filtered_data_length{filtered_data_length}')
      
    #提取筛选后数据的某一属性
    start_load_times = [traffic.loadertime1 for traffic in filtered_traffic]
    stop_load_times = [traffic.loadertime2 for traffic in filtered_traffic]
    loader_task = [traffic.loadertime2 for traffic in filtered_traffic]
    #计算装载时间
    # load_time = [(start_load_time - stop_load_time).total_seconds()]
    load_time = [(start_load_time - stop_load_time).total_seconds() for \
                 start_load_time, stop_load_time in zip(start_load_times, stop_load_times)]
    logging.debug(f'load_time{load_time}')

    for i in range(filtered_data_length): 
        per_second_weight += loader_task[i] / load_time[i] * 1.0  
      
    per_second_weight /= filtered_data_length
    current_load_weight = per_second_weight * time_difference
    
    return current_load_weight
