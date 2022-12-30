import os
import pandas as pd
import numpy as np
import json
from classes.objects import Airport, Runway, Aircraft, Flight
from copy import deepcopy
# from classes.objects import Runway
def create_airport(file_name):
    i = 1
    root_path = os.getcwd() + f"\\{file_name}.xlsx"
    excel_data = pd.ExcelFile(root_path)
    sheet_names = excel_data.sheet_names
    excel_data = pd.read_excel(root_path, sheet_name=sheet_names[0])
    # excel_data = excel_data.replace(np.nan, 'None')
    data_dict = excel_data.to_dict(orient='dict')
    airport_objects = []
    airport_created = False
    for index in data_dict['Name']:
        if type(data_dict['Name'][index]) == str:
            if airport_created:
                airport_obj.aircrafts = aircrafts
                airport_obj.runways = runways
                airport_objects.append(deepcopy(airport_obj))
            airport_obj = Airport(i, [], [], json.loads(data_dict['Position'][index]), data_dict['Name'][index])
            airport_created = True
            runways = []
            aircrafts = []
            i += 1
            if not np.isnan(data_dict['RunwayDirection'][index]):
                runway_obj = Runway(i, data_dict['RunwayDirection'][index], data_dict['RunwayLength'][index], data_dict['RunwayWidth'][index], 
                                    data_dict['Runway'][index] if type(data_dict['Runway'][index]) == str else 'runway with no name',
                                    json.loads(data_dict['PositionStart'][index]))
                runways.append(runway_obj)
                i += 1
            if not np.isnan(data_dict['AircraftNumber'][index]):
                for n in range(int(data_dict['AircraftNumber'][index])):
                    aircrafts.append(Aircraft(i, data_dict['AircraftID'][index], None, 'ready', [], airport_obj.position))
                    i += 1
        elif np.isnan(data_dict['Name'][index]):
            if not np.isnan(data_dict['RunwayDirection'][index]):
                runway_obj = Runway(i, data_dict['RunwayDirection'][index], data_dict['RunwayLength'][index], data_dict['RunwayWidth'][index], 
                                    data_dict['Runway'][index] if type(data_dict['Runway'][index]) == str else 'runway with no name',
                                    json.loads(data_dict['PositionStart'][index]))
                runways.append(runway_obj)
                i += 1
            if not np.isnan(data_dict['AircraftNumber'][index]):
                for n in range(data_dict['AircraftNumber'][index]):
                    aircrafts.append(Aircraft(i, data_dict['AircraftID'][index], None, 'ready', [], runway_obj.position))
                    i += 1
    airport_obj.runways = runways
    airport_objects.append(deepcopy(airport_obj))
    last_id = i
    return airport_objects, last_id


def create_flights(trip_schedule_data, last_id):
    flights = []
    for i in range(len(trip_schedule_data['trip_start_time'])):
        flights.append(Flight(last_id, trip_schedule_data['origin_id'][i], trip_schedule_data['destination_id'][i], 
                              trip_schedule_data['trip_start_time'][i], None, None))
        last_id += 1
    return flights, last_id
        
# def create_aircrafts(file_name, last_id):
#     root_path = os.getcwd() + f"\\{file_name}.xlsx"
#     excel_data = pd.ExcelFile(root_path)
#     excel_data = pd.read_excel(root_path, sheet_name = excel_data.sheet_names[0])
#     excel_data = excel_data.replace(np.nan, 'None')
#     data_dict = excel_data.to_dict(orient='dict')
#     aircraft_ids = data_dict['aircraft_id']
#     arrival_datetimes = data_dict['arrival_datetime']
#     arrival_epochs = data_dict['arrival_epoch']
#     toward_angles = data_dict['toward_angle']
#     aircraft_objects = []
#     status = ''
#     for i in aircraft_ids:
#         aircraft_objects.append(Aircraft(toward_angles[i], status, arrival_epochs[i], last_id+1))
#         last_id += 1
#     return aircraft_objects, last_id        