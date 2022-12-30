import pandas as pd
import numpy as np
from datetime import datetime
def create_schedule(airports, number_of_trips, start_time, end_time, output_file_name):
    duration = end_time-start_time
    trip_start_time_list = []
    datetime_list = []
    heading_toward_angle_list = []
    destination_id_list = []
    origin_id_list = []
    # aircraft_id_list = []
    for trip in range(number_of_trips):
        trip_start_time = int(np.random.rand() * duration + start_time)
        # arrival_time_list.append(arrivial_time)
        origin_index = int(np.random.rand()*len(airports))
        destination_index = int(np.random.rand()*len(airports))
        while destination_index == origin_index:
            destination_index = int(np.random.rand()*len(airports))
        origin_id = airports[origin_index].id_
        destination_id = airports[destination_index].id_
        # aircraft_id_list.append(aircraft)
        
        trip_start_time_list.append(trip_start_time)
        origin_id_list.append(origin_id)
        destination_id_list.append(destination_id)
    origin_id_list = [x for _,x in sorted(zip(trip_start_time_list,origin_id_list))]
    destination_id_list = [x for _,x in sorted(zip(trip_start_time_list,destination_id_list))]
    # aircraft_id_list = [i for i in range(number_of_aircrafts)]
    trip_start_time_list.sort()
    datetime_list = [datetime.fromtimestamp(i).strftime('%Y-%m-%d %H:%M:%S') for i in trip_start_time_list]
    data = {'trip_start_time':trip_start_time_list,
            'origin_id': origin_id_list,
            'destination_id': destination_id_list,
            'datetime':datetime_list}
    df = pd.DataFrame(data)
    writer=pd.ExcelWriter('{0}.xlsx'.format(str(output_file_name)), engine='xlsxwriter')
    df.to_excel(writer,sheet_name='arrival_time')
    writer.save()
    return data
        