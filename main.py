from classes.objects import Airport, Runway, Aircraft, Flight
from create_objects import create_airport, create_flights
from create_schedule import create_schedule
from run_simulation_new import run_simulation
import pandas as pd

file_name = 'airport_info'
airport_objects, last_id = create_airport(file_name)
schedule_file_name = 'aircraft_schedule_info'
number_of_trips = 100
start_time = 1668832200
# end_time = 1668832200 + 7200
end_time = 1668886200
landing_occupation_time = 180 #seconds
takeoff_occupation_time = 120 #seconds
turnaround_time = 600 #seconds
maximum_fligh_delay = 6000 # seconds
aircrafts_per_day = 100
holding_duration = 600 #seconds
waiting_at_gate_duration = 1800 #seconds
delta_time_to_reserve_landing = 600 # seconds

climb_speed = 250 # knots
aircraft_climb_rate = 3000 # ft/min
cruise_altitude = 25000 # ft
cruise_speed = 450 # knots
aircraft_info = {1:{'climb_speed':climb_speed, 'climb_rate':aircraft_climb_rate, 
                    'cruise_altitude':cruise_altitude, 'cruise_speed':cruise_speed,
                    'descent_speed':200, 'descent_rate':3000}}
trip_schedule_data = create_schedule(airport_objects, number_of_trips, start_time, end_time, schedule_file_name)
flights, last_id = create_flights(trip_schedule_data, last_id)
airports, flights, msg_list, current_epoch = run_simulation(airport_objects, flights, landing_occupation_time, takeoff_occupation_time, turnaround_time, \
                      holding_duration, waiting_at_gate_duration, aircraft_info, delta_time_to_reserve_landing, maximum_fligh_delay, start_time, end_time + 3600)
def extract_data(flights):
    data = {'before_takeoff':0, 'before_turnaround':0, 'before_landing':0}
    for flight in flights:
        data['before_takeoff'] += flight.delayed_at['before_takeoff']/60
        data['before_turnaround'] += flight.delayed_at['before_turnaround']/60
        data['before_landing'] += flight.delayed_at['before_landing']/60
    return data
            
# writer=pd.ExcelWriter('{0}.xlsx'.format('flight_data'), engine='xlsxwriter')
# for maximum_fligh_delay in [300, 600, 900, 1200, 1500, 1800]:
#     print(maximum_fligh_delay)
#     flight_delay_list = []
#     holding_delay_list = []
#     gate_delay_list = []
#     number_of_trip_list = []
#     success_list = []
#     simulation_time_list = []
#     for number_of_trips in [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145]:
#         print(number_of_trips)
#         file_name = 'airport_info'
#         airport_objects, last_id = create_airport(file_name)
#         schedule_file_name = 'aircraft_schedule_info'
#         start_time = 1668832200
#         # end_time = 1668832200 + 7200
#         end_time = 1668886200
#         landing_occupation_time = 180 #seconds
#         takeoff_occupation_time = 120 #seconds
#         turnaround_time = 600 #seconds
#         # maximum_fligh_delay = 1200 # seconds
#         aircrafts_per_day = 100
#         holding_duration = 600 #seconds
#         waiting_at_gate_duration = 1800 #seconds
#         delta_time_to_reserve_landing = 600 # seconds
        
#         climb_speed = 250 # knots
#         aircraft_climb_rate = 3000 # ft/min
#         cruise_altitude = 25000 # ft
#         cruise_speed = 450 # knots
#         aircraft_info = {1:{'climb_speed':climb_speed, 'climb_rate':aircraft_climb_rate, 
#                             'cruise_altitude':cruise_altitude, 'cruise_speed':cruise_speed,
#                             'descent_speed':200, 'descent_rate':3000}}
#         trip_schedule_data = create_schedule(airport_objects, number_of_trips, start_time, end_time, schedule_file_name)
#         flights, last_id = create_flights(trip_schedule_data, last_id)
#         airports, flights, msg_list, current_epoch = run_simulation(airport_objects, flights, landing_occupation_time, takeoff_occupation_time, turnaround_time, \
#                               holding_duration, waiting_at_gate_duration, aircraft_info, delta_time_to_reserve_landing, maximum_fligh_delay, start_time, end_time + 3600)
#         data = extract_data(flights)
#         success_list.append(False if msg_list else True)
#         number_of_trip_list.append(number_of_trips)
#         gate_delay_list.append(data['before_takeoff'])
#         holding_delay_list.append(data['before_landing'])
#         flight_delay_list.append(data['before_turnaround'])
#         simulation_time_list.append((current_epoch-start_time)/60)
#     df=pd.DataFrame({'number of trips':number_of_trip_list,
#                       'at gate delay':gate_delay_list,
#                       'holding delay': holding_delay_list,
#                       'flight delay': flight_delay_list,
#                       'success': success_list,
#                       'end_of_simulation_after':simulation_time_list})
#     # writer=pd.ExcelWriter('{0}.xlsx'.format(str(output_file_name)), engine='xlsxwriter')
#     df.to_excel(writer,sheet_name=str(maximum_fligh_delay))
# writer.save()