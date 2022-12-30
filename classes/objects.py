import numpy as np
class Airport:
    def __init__(self, id_, runways, aircrafts, position, name):
        self.id_ = id_
        self.runways = runways
        self.position = position
        self.name = name
        self.aircrafts = aircrafts
        
class Runway:
    def __init__(self, id_, direction, length, width, name, position_start):
        self.id_ = id_
        self.direction = direction #degree
        self.length = length #ft
        self.width = width #ft
        self.name = name
        self.status = 'ready'
        self.status_period_epochs = []
        self.occupied_aircraft = None
        self.position_start = position_start
        self.position_end =[]
        self.position_end.append(position_start[0] + (length*0.000164579)*np.cos(direction*np.pi/180))
        self.position_end.append(position_start[1] + (length*0.000164579)*np.sin(direction*np.pi/180))

class Aircraft:
    def __init__(self, id_, db_id, destination_id, status, schedule_list, position):
        self.id_ = id_
        self.destination_id = destination_id
        self.status = status
        self.schedule_list = schedule_list
        self.position = position
        self.db_id = db_id

class Flight:
    def __init__(self, id_, origin_id, destiation_id, start_time, carrier_kind, carrier_id):
        self.id_ = id_
        self.origin_id = origin_id
        self.destiation_id = destiation_id
        self.start_time = start_time
        self.carrier_kind = carrier_kind
        self.carrier_id = carrier_id
        self.status = 'scheduled'