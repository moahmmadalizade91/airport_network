from classes.objects import Airport, Runway, Aircraft, Flight
from create_objects import create_airport, create_flights
from create_schedule import create_schedule

file_name = 'airport_info'
airport_objects, last_id = create_airport(file_name)
schedule_file_name = 'aircraft_schedule_info'
number_of_trips = 20
start_time = 1668832200
end_time = 1668886200
trip_schedule_data = create_schedule(airport_objects, number_of_trips, start_time, end_time, schedule_file_name)
flights, last_id = create_flights(trip_schedule_data, last_id)