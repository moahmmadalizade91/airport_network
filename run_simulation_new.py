from math import sqrt
from copy import deepcopy


def object_finder(objects, attribute_dict):
    out_obj = []
    for obj in objects:
        for attribute in attribute_dict:
            if getattr(obj, attribute) == attribute_dict[attribute]:
                out_obj = [obj]
            else:
                out_obj = []
                break
        if out_obj:
            break
    if not out_obj:
        out_obj = ['object not found']
    return out_obj


def distnace_calculator(point1, point2):
    distance = sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    return distance


def find_nearest_runway(airport_obj, arrival_angle):
    minimum_angle_deviation = 361
    reference_runway_id = None
    for runway in airport_obj.runways:
        if abs(runway.direction - arrival_angle) < minimum_angle_deviation and runway.status.lower() == 'ready':
            reference_runway_id = runway.id_
            minimum_angle_deviation = runway.direction - arrival_angle
    return reference_runway_id, minimum_angle_deviation


def find_sorted_runways(mode, current_epoch, airports, flight, takeoff_occupation_time, landing_occupation_time):
    origin_airport = object_finder(airports, {'id_':flight.origin_id})[0]
    destination_airport = object_finder(airports, {'id_':flight.destination_id})[0]
    runway_id_list = []
    distance_list = []
    if mode.lower() == 'takeoff':
        reference_delta_time = takeoff_occupation_time
        reference_position = destination_airport.position
    elif mode.lower() == 'landing':
        reference_delta_time = landing_occupation_time
        reference_position = origin_airport.position
    for runway in origin_airport.runways:
        flag_1 = flag_2 = flag_3 = False
        for time_schedule in runway.schedule_list:
            flag_1 = time_schedule['t_0'] <= current_epoch <= time_schedule['t_f']
            flag_2 = time_schedule['t_0'] <= current_epoch + reference_delta_time <= time_schedule['t_f']
            flag_3 = current_epoch <= time_schedule['t_0'] and current_epoch + reference_delta_time >= time_schedule['t_f']
        if not flag_1 and not flag_2 and not flag_3:
            runway_id_list.append(runway.id_)
            distance_list.append(distnace_calculator(runway.position_end, reference_position))
            # if time_schedule['t_0'] <= current_epoch <= time_schedule['t_f']
        # if runway.status.lower() == 'ready':
            # runway_id_list.append(runway.id_)
            # distance_list.append(distnace_calculator(runway.position_end, destination_airport.position))
    runway_id_list = [x for _,x in sorted(zip(distance_list,runway_id_list))]
    return runway_id_list
    

def create_flight_schedule_for_starting_aircraft(flight, aircraft, aircraft_info, start_time, takeoff_occupation_time, airports):
    schedule_list = []
    climb_speed = aircraft_info[aircraft.db_id]['climb_speed'] # knots
    aircraft_climb_rate = aircraft_info[aircraft.db_id]['climb_rate'] # ft/min
    cruise_altitude = aircraft_info[aircraft.db_id]['cruise_altitude'] # ft
    cruise_speed = aircraft_info[aircraft.db_id]['cruise_speed'] # knots
    # takeoff section
    takeoff_runway_id = flight.takeoff_runway
    origin_airport = object_finder(airports, {'id_':flight.origin_id})[0]
    takeoff_runway = object_finder(origin_airport.runways, {'id_':takeoff_runway_id})[0]
    schedule_list.append({'t_0':start_time, 't_f': start_time + takeoff_occupation_time, 'type':'takeoff', 'flight':flight.id_,
                          'distance':0})
    # climb section
    start_time += takeoff_occupation_time
    climb_duration = (cruise_altitude/aircraft_climb_rate) * 60 # seconds
    climb_ground_speed =  sqrt(climb_speed**2 - (aircraft_climb_rate*0.00987473)**2) # knots
    climb_distance = (climb_duration/3600)*climb_ground_speed # nautical mile
    schedule_list.append({'t_0':start_time, 't_f': start_time + climb_duration, 'type':'climb', 'flight':flight.id_, 'distance':climb_distance})
    # cruise section
    start_time += climb_duration
    destination_airport = object_finder(airports, {'id_':flight.destination_id})[0]
    total_distance = distnace_calculator(takeoff_runway.position_end, destination_airport.position)
    cruise_distance = total_distance - 2*climb_distance
    cruise_duration = (cruise_distance/cruise_speed)*3600
    schedule_list.append({'t_0':start_time, 't_f': start_time + cruise_duration, 'type':'cruise', 'flight':flight.id_, 'distance':cruise_distance})
    return schedule_list, total_distance


def create_flight_schedule_for_landing_aircraft(flight, aircraft, current_time, aircraft_info, landing_occupation_time, airports):
    schedule_list = []
    descent_speed = aircraft_info[aircraft.db_id]['descent_speed'] # knots
    aircraft_descent_rate = aircraft_info[aircraft.db_id]['descent_rate'] # ft/min
    cruise_altitude = aircraft_info[aircraft.db_id]['cruise_altitude'] # ft
    cruise_speed = aircraft_info[aircraft.db_id]['cruise_speed'] # knots
    holding_schedule = find_object_schedule_by_type(aircraft, 'holding')
    cruise_schedule = find_object_schedule_by_type(aircraft, 'cruise')
    total_distance = flight.total_distance
    passed_distance = 0
    for schedule in aircraft.schedule_list:
        passed_distance += schedule['distance']
    if not holding_schedule:
        start_time = cruise_schedule['t_f']
    else:
        start_time = current_time
    # descent section
    descent_duration = (cruise_altitude/aircraft_descent_rate) * 60 # seconds
    descent_ground_speed =  sqrt(descent_speed**2 - (aircraft_descent_rate*0.00987473)**2) # knots
    descent_distance = (descent_duration/3600)*descent_ground_speed # nautical mile
    schedule_list.append({'t_0':start_time, 't_f': start_time + descent_duration, 'type':'descent', 'flight':flight.id_, 'distance':descent_distance})
    # landing section
    start_time += descent_duration
    schedule_list.append({'t_0':start_time, 't_f': start_time + landing_occupation_time, 'type':'landing', 'flight':flight.id_,
                          'distance':0})
    return schedule_list
    

def find_object_schedule_by_type(obj, schedule_type):
    for time_schedule in obj.schedule_list:
        if time_schedule['type'].lower() == schedule_type:
            return time_schedule
    return {}


def move_aircaft_obj_to_destination_airport(aircraft_obj_id, airports, flight):
    origin_airport = object_finder(airports, {'id_':flight.origin_id})[0]
    destination_airport = object_finder(airports, {'id_':flight.destination_id})[0]
    for i in range(len(origin_airport.aircrafts)):
        if aircraft_obj_id == origin_airport.aircrafts[i].id_:
            to_be_deleted_index = i
            break
    destination_airport.aircrafts.append(deepcopy(origin_airport.aircrafts[to_be_deleted_index]))
    del origin_airport.aircrafts[to_be_deleted_index]
    return airports

def physics_module(airports, flights, current_epoch, turnaround_time, takeoff_occupation_time, landing_occupation_time, \
                   holding_duration, waiting_at_gate_duration, delta_time_to_reserve_landing, maximum_fligh_delay, aircraft_info):
    msg_list = []
    for flight in flights:
        if flight.status.lower() in ['descent', 'landing']:
            airport_obj = object_finder(airports, {'id_':flight.destination_id})[0]
        else:
            airport_obj = object_finder(airports, {'id_':flight.origin_id})[0]
        if flight.status.lower() == 'scheduled' and current_epoch >= flight.start_time - turnaround_time:
            # if current_epoch >= flight.start_time:
            #     msg_list.append('too much delay for flight with id {0}'.format(flight.id_))
            #     return airports, flights, msg_list
            for aircraft in airport_obj.aircrafts:
                if aircraft.status.lower() == 'ready':
                    aircraft.schedule_list.append({'t_0':current_epoch, 't_f': current_epoch + turnaround_time, 
                                                   'type':'turnaround', 'flight':flight.id_, 'distance':0})
                    flight.status = aircraft.status = 'turnaround'
                    flight.carrier_kind = 'aircraft'
                    flight.carrier_id = aircraft.id_
                    break
            if flight.status.lower() == 'scheduled':
                flight.delayed_at['before_turnaround'] += 1
        elif flight.status.lower() == 'turnaround':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            turnaround_schedule = find_object_schedule_by_type(aircraft_obj, 'turnaround')
            if current_epoch >= turnaround_schedule['t_f']:
                runway_id_list = find_sorted_runways('takeoff', current_epoch, airports, flight, takeoff_occupation_time, landing_occupation_time)
                if runway_id_list:
                    runway_obj = object_finder(airport_obj.runways, {'id_':runway_id_list[0]})[0]
                    # aircraft = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
                    flight.status = 'takeoff'
                    flight.takeoff_runway = runway_id_list[0]
                    flight_schedule, total_distance = create_flight_schedule_for_starting_aircraft(flight, aircraft_obj, aircraft_info, \
                                                                                   current_epoch, takeoff_occupation_time, airports)
                    aircraft_obj.schedule_list += flight_schedule
                    aircraft_obj.status = 'takeoff'
                    # runway_obj.status = 'takeoff'
                    takeoff_schedule = find_object_schedule_by_type(aircraft_obj, 'takeoff')
                    runway_obj.schedule_list += [takeoff_schedule]
                else:
                    flight.delayed_at['before_takeoff'] += 1
        elif flight.status.lower() == 'takeoff':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            takeoff_schedule = find_object_schedule_by_type(aircraft_obj, 'takeoff')
            if current_epoch >= takeoff_schedule['t_f']:
                # runway_obj = object_finder(airport_obj.runways, {'id_':flight.takeoff_runway})[0]
                # runway_obj.status = 'ready'
                aircraft_obj.status = flight.status = 'climb'
        elif flight.status.lower() == 'climb':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            climb_schedule = find_object_schedule_by_type(aircraft_obj, 'climb')
            if current_epoch >= climb_schedule['t_f']:
                aircraft_obj.status = flight.status = 'cruise'
        elif flight.status.lower() == 'cruise':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            cruise_schedule = find_object_schedule_by_type(aircraft_obj, 'cruise')
            descent_schedule = find_object_schedule_by_type(aircraft_obj, 'descent')
            if not descent_schedule and current_epoch >= cruise_schedule['t_f'] - delta_time_to_reserve_landing:
            # if current_epoch >= cruise_schedule['t_f'] - delta_time_to_reserve_landing:
                after_cruise_schedule = create_flight_schedule_for_landing_aircraft(flight, aircraft_obj, cruise_schedule['t_f'], 
                                                                                    aircraft_info, landing_occupation_time, airports)
                for schedule in after_cruise_schedule:
                    if schedule['type'].lower() == 'landing':
                        landing_schedule = schedule
                        break
                runway_id_list = find_sorted_runways('landing', landing_schedule['t_0'], airports, flight, takeoff_occupation_time, 
                                                     landing_occupation_time)
                if runway_id_list:
                    runway_obj = object_finder(airport_obj.runways, {'id_':runway_id_list[0]})[0]
                    flight.takeoff_runway = runway_id_list[0]
                    aircraft_obj.schedule_list += after_cruise_schedule
                    runway_obj.schedule_list += [landing_schedule]
                    # aircraft_obj.status = 'descent'
                    # airports = move_aircaft_obj_to_destination_airport(aircraft_obj.id_, airports, flight)
                elif current_epoch >= cruise_schedule['t_f']:
                    aircraft_obj.schedule_list += [{'t_0':current_epoch, 't_f': current_epoch + holding_duration, 
                                                   'type':'holding', 'flight':flight.id_, 'distance':0}]
                    aircraft_obj.status = flight.status = 'holding'
            elif descent_schedule and current_epoch >= cruise_schedule['t_f']:
                aircraft_obj.status = flight.status = 'descent'
                airports = move_aircaft_obj_to_destination_airport(aircraft_obj.id_, airports, flight)
        elif flight.status.lower() == 'holding':
            flight.delayed_at['before_landing'] += 1
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            cruise_schedule = find_object_schedule_by_type(aircraft_obj, 'cruise')
            # holding_schedule = find_object_schedule_by_type(aircraft_obj, 'holding')
            # if current_epoch >= holding_schedule['t_f']:
            #     msg_list.append('too much holding for flight with id {0}'.format(flight.id_))
            #     return None, None, msg_list
            after_cruise_schedule = create_flight_schedule_for_landing_aircraft(flight, aircraft_obj, cruise_schedule['t_f'], 
                                                                                aircraft_info, landing_occupation_time, airports)
            for schedule in after_cruise_schedule:
                if schedule['type'].lower() == 'landing':
                    landing_schedule = schedule
                    break
            runway_id_list = find_sorted_runways('landing', landing_schedule['t_0'], airports, flight, takeoff_occupation_time, 
                                                     landing_occupation_time)
            if runway_id_list:
                for schedule in aircraft_obj.schedule_list:
                    if schedule['type'].lower() == 'holding':
                        schedule['t_f'] = current_epoch
                runway_obj = object_finder(airport_obj.runways, {'id_':runway_id_list[0]})[0]
                flight.takeoff_runway = runway_id_list[0]
                aircraft_obj.schedule_list += after_cruise_schedule
                runway_obj.schedule_list += [landing_schedule]
                aircraft_obj.status = flight.status = 'descent'
                airports = move_aircaft_obj_to_destination_airport(aircraft_obj.id_, airports, flight)
        elif flight.status.lower() == 'descent':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            descent_schedule = find_object_schedule_by_type(aircraft_obj, 'descent')
            if current_epoch >= descent_schedule['t_f']:
                aircraft_obj.status = flight.status = 'landing'
        elif flight.status.lower() == 'landing':
            aircraft_obj = object_finder(airport_obj.aircrafts, {'id_':flight.carrier_id})[0]
            landing_schedule = find_object_schedule_by_type(aircraft_obj, 'landing')
            if current_epoch >= landing_schedule['t_f']:
                aircraft_obj.status = 'ready'
                aircraft_obj.schedule_list = []
                flight.status = 'done'
                # else:
                #     holding_schedule = find_object_schedule_by_type(aircraft_obj, 'holding')
                    
        if flight.delayed_at['before_takeoff'] > waiting_at_gate_duration:
            msg_list.append('too much at gate delay for flight with id {0}'.format(flight.id_))
            # return airports, flights, msg_list
        elif flight.delayed_at['before_landing'] > holding_duration:
            msg_list.append('too much holding delay for flight with id {0}'.format(flight.id_))
            # return airports, flights, msg_list
        elif flight.delayed_at['before_turnaround'] > maximum_fligh_delay:
            msg_list.append('too much delay for flight with id {0}'.format(flight.id_))
            # return airports, flights, msg_list
                
        # elif flight.status.lower() == 'turnaround':
        #     if r
    return airports, flights, msg_list

def run_simulation(airports, flights, landing_occupation_time, takeoff_occupation_time, turnaround_time, \
                   holding_duration, waiting_at_gate_duration, aircraft_info, delta_time_to_reserve_landing, maximum_fligh_delay, start_time, end_time):
    current_epoch = start_time
    while current_epoch <= end_time:
        # if current_epoch%100 == 0:
        #     print(current_epoch)
        airports, flights, msg_list = physics_module(airports, flights, current_epoch, turnaround_time, takeoff_occupation_time, landing_occupation_time, \
                                           holding_duration, waiting_at_gate_duration, delta_time_to_reserve_landing, maximum_fligh_delay, aircraft_info)
        if msg_list:
            break
        current_epoch += 1
    # if flights is None:
    #     return airports, flights, msg_list
    # else:
    return airports, flights, msg_list, current_epoch
        