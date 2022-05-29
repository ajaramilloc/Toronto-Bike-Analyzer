"""
 * Copyright 2020, Departamento de sistemas y Computación,
 * Universidad de Los Andes
 *
 *
 * Desarrolado para el curso ISIS1225 - Estructuras de Datos y Algoritmos
 *
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along withthis program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Contribuciones:
 *
 * Dario Correal - Version inicial
 """

import config as cf
from DISClib.ADT import graph as gr
from DISClib.ADT import stack
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.Algorithms.Sorting import mergesort as merge
import time
assert cf

# -----------------------------------------------------
# NEW ANALYZER
# -----------------------------------------------------

def newAnalyzer():
    
    analyzer = {
        'connections': None,
        'stops': None,
        'trip_routes': None,
        'paths': None,
        'stations_ids': None,
        'stations_formats': None,
        'trips_dates': None,
        'bikes_trips': None,
        'out_stations': None
    }

    analyzer['stops'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # stops info with average duration
    analyzer['trip_routes'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # key -> trip id / value -> trip info
    analyzer['stations_ids'] = mp.newMap(790, maptype='PROBING', loadfactor=0.5) # key -> station name / value -> station id
    analyzer['stations_formats'] = mp.newMap(790, maptype='PROBING', loadfactor=0.5)
    analyzer['trips_dates'] = om.newMap(omaptype='RBT', comparefunction=compareDates) # trips by dates
    analyzer['bikes_trips'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # bikes info
    analyzer['out_stations'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000) # graph 

    return analyzer

def addStopConnection(analyzer, trip):
    # Format stations names
    origin = trip['Start Station Name']
    if trip['Start Station Name'] == '':
        trip['Start Station Name'] = 'UNKNOWN'
    origin_id = float(trip['Start Station Id'])
    origin_format = f'{origin_id}-{origin}'
    arrival = trip['End Station Name']
    if trip['End Station Name'] == '':
        trip['End Station Name'] = 'UNKNOWN'
    arrival_id = float(trip['End Station Id'])
    arrival_format = f'{arrival_id}-{arrival}'
    # Format trips dates
    trip_date = trip['Start Time'].split(' ')[0]
    init_trip_hour = trip['Start Time'].split(' ')[1]
    finish_trip_hour = trip['End Time'].split(' ')[1]
    # Add vertices to the graph
    addStop(analyzer, origin_format)
    addStop(analyzer, arrival_format)
    # Add average of the trip
    addRoutes(analyzer, origin_format, arrival_format, trip)
    # Add the trip id the the trips map
    addTrip(analyzer, trip)
    # Add the station id in the stations formats map
    addStationId(analyzer, origin_format, trip['Start Station Id'])
    addStationId(analyzer, arrival_format, trip['End Station Id'])
    # Add the station format in the stations names map
    addStationFormat(analyzer, origin, origin_format)
    addStationFormat(analyzer, arrival, arrival_format)

    addOutTrips(analyzer, origin_format, trip_date, init_trip_hour, trip)
    # Add trips by date
    addTripsByDate(analyzer, trip_date, init_trip_hour, finish_trip_hour, trip, origin_format, arrival_format)
    # Add the bike info in the structures
    addBikeInfo(analyzer, trip['Bike Id'], trip, origin_format, arrival_format)

def addStop(analyzer, stop):
    """
    Add a vertex to the graph
    """
    if not gr.containsVertex(analyzer['connections'], stop):
        gr.insertVertex(analyzer['connections'], stop)

def addRoutes(analyzer, origin_format, destination_format, trip):
    """
    For each trip calculates and add the average duration
    """
    if mp.contains(analyzer['stops'], origin_format):
        origin_station = me.getValue(mp.get(analyzer['stops'], origin_format))
        if mp.contains(origin_station, destination_format):
            arrival_station = me.getValue(mp.get(origin_station, destination_format))
            arrival_station[2] += 1
            arrival_station[1] += int(trip['Trip  Duration'])
            arrival_station[0] = arrival_station[1] / arrival_station[2]

        else:
            addArrival(origin_station, destination_format, trip['Trip  Duration'], trip['Trip Id'])
        
    else:
        arrivals = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
        addArrival(arrivals, destination_format, trip['Trip  Duration'], trip['Trip Id'])
        mp.put(analyzer['stops'], origin_format, arrivals)

def addArrival(map, destination, trip_duration, trip_id):
    """
    Add a list to the trip, pos 0: Average / pos 1: Durations sum / pos 2: Total trips / pos 3: list with trips ids
    """
    trip_duration = int(trip_duration)
    trips_ids = lt.newList('ARRAY_LIST')
    lt.addLast(trips_ids, trip_id)
    durations = [trip_duration, trip_duration, 1, trips_ids]
    mp.put(map, destination, durations)

def addTrip(analyzer, trip):
    """
    Add the trip id in the trip_routes map. (key -> Trip Id / value -> trip info)
    """
    mp.put(analyzer['trip_routes'], trip['Trip Id'], trip)

def addStationId(analyzer, station, station_id):
    """
    Add the station name in the stations_ids map. (key -> Station Name / value -> Station Id)
    """
    if mp.contains(analyzer['stations_ids'], station):
        pass
    else:
        mp.put(analyzer['stations_ids'], station, station_id)

def addStationFormat(analyzer, station, station_format):
    if mp.contains(analyzer['stations_formats'], station):
        pass
    else:
        mp.put(analyzer['stations_formats'], station, station_format)

def addTripsByDate(analyzer, trip_date, init_trip_hour, finish_trip_hour, trip, origin_format, arrival_format):
    
    if om.contains(analyzer['trips_dates'], trip_date):
        date = me.getValue(mp.get(analyzer['trips_dates'], trip_date))

        date_info = me.getValue(mp.get(date, 'date_info'))
        date_info[0] += 1
        date_info[1] += int(trip['Trip  Duration'])

        # Initial Hours Info
        initial_hours = me.getValue(mp.get(date, 'initial_hours'))
        format = init_trip_hour.split(':')[0]
        init_format = f'{format}:00 - {format}:59'
        if mp.contains(initial_hours, init_format):
            initial_count = me.getValue(mp.get(initial_hours, init_format))
            initial_count[0] += 1
        else:
            mp.put(initial_hours, init_format, [1])

        # Finish Hours Info
        finish_hours = me.getValue(mp.get(date, 'finish_hours'))
        format = finish_trip_hour.split(':')[0]
        finish_format = f'{format}:00 - {format}:59'
        if mp.contains(finish_hours, finish_format):
            finish_count = me.getValue(mp.get(finish_hours, finish_format))
            finish_count[0] += 1
        else:
            mp.put(finish_hours, finish_format, [1]) 

        # Origin Stations Info
        origin_stations = me.getValue(mp.get(date, 'origin_stations'))
        if mp.contains(origin_stations, origin_format):
            origin_station = me.getValue(mp.get(origin_stations, origin_format))
            origin_station[0] += 1
        else:
            mp.put(origin_stations, origin_format, [1])

        # Arrival Stations Info
        arrival_stations = me.getValue(mp.get(date, 'arrival_stations'))
        if mp.contains(arrival_stations, arrival_format):
            arrival_station = me.getValue(mp.get(arrival_stations, arrival_format))
            arrival_station[0] += 1
        else:
            mp.put(arrival_stations, arrival_format, [1])
    else:
        dates = mp.newMap(6, maptype='PROBING', loadfactor=0.5)
        date_info = [1, int(trip['Trip  Duration'])]
        mp.put(dates, 'date_info', date_info)

        # Initial Hours Info
        initial_hours = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        format = init_trip_hour.split(':')[0]
        init_format = f'{format}:00 - {format}:59'
        mp.put(initial_hours, init_format, [1])
        mp.put(dates, 'initial_hours', initial_hours)

        # Finish Hours Info
        finish_hours = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        format = finish_trip_hour.split(':')[0]
        finish_format = f'{format}:00 - {format}:59'
        mp.put(finish_hours, finish_format, [1])
        mp.put(dates, 'finish_hours', finish_hours)

        # Origin Stations Info
        origin_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(origin_stations, origin_format, [1])
        mp.put(dates, 'origin_stations', origin_stations)

        # Arrival Stations Info
        arrival_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(arrival_stations, arrival_format, [1])
        mp.put(dates, 'arrival_stations', arrival_stations)

        mp.put(analyzer['trips_dates'], trip_date, dates)

def addOutTrips(analyzer, origin_format, trip_date, init_trip_hour, trip):
    if mp.contains(analyzer['out_stations'], origin_format):
        station_info = me.getValue(mp.get(analyzer['out_stations'], origin_format))

        suscribers_count = me.getValue(mp.get(station_info, 'suscribers_count'))
        tourists_count = me.getValue(mp.get(station_info, 'tourists_count'))
        total_count = me.getValue(mp.get(station_info, 'total_count'))
        total_count[0] += 1
        if trip['User Type'] == 'Annual Member':
            suscribers_count[0] += 1
        else:
            tourists_count[0] += 1

        out_hours = me.getValue(mp.get(station_info, 'out_hours'))
        format = init_trip_hour.split(':')[0]
        hour_format = f'{format}:00 - {format}:59'
        if mp.contains(out_hours, hour_format):
            hour = me.getValue(mp.get(out_hours, hour_format))
            hour[0] += 1
        else:
            mp.put(out_hours, hour_format, [1])

        num_trips = me.getValue(mp.get(station_info, 'num_trips'))
        if mp.contains(num_trips, trip_date):
            date = me.getValue(mp.get(num_trips, trip_date))
            date[0] += 1
        else:
            mp.put(num_trips, trip_date, [1])

    else:
        station_info = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        suscribers_count = [0]
        tourists_count = [0]
        total_count = [1]
        if trip['User Type'] == 'Annual Member':
            suscribers_count[0] += 1
        else:
            tourists_count[0] += 1

        mp.put(station_info, 'suscribers_count', suscribers_count)
        mp.put(station_info, 'tourists_count', tourists_count)
        mp.put(station_info, 'total_count', total_count)

        format = init_trip_hour.split(':')[0]
        hour_format = f'{format}:00 - {format}:59'

        out_hours = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        mp.put(out_hours, hour_format, [1])
        mp.put(station_info, 'out_hours', out_hours)

        num_trips = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        mp.put(num_trips, trip_date, [1])
        mp.put(station_info, 'num_trips', num_trips)

        mp.put(analyzer['out_stations'], origin_format, station_info)

def addBikeInfo(analyzer, bike_id, trip, origin_format, arrival_format):
    """
    - Add the bike id in the map bikes_trips
    - Add the total trips and total duration with the bike
    - Add the origin and arrival stations of the bike
    - Each station have the total trips
    """
    if mp.contains(analyzer['bikes_trips'], bike_id):
        bike = me.getValue(mp.get(analyzer['bikes_trips'], bike_id))

        bike_info = me.getValue(mp.get(bike, 'bike_info'))
        bike_info[0] += 1
        bike_info[1] += int(trip['Trip  Duration'])

        origin_stations = me.getValue(mp.get(bike, 'origin_stations'))
        if mp.contains(origin_stations, origin_format):
            origin_station = me.getValue(mp.get(origin_stations, origin_format))
            origin_station[0] += 1
        else:
            mp.put(origin_stations, origin_format, [1])

        arrival_stations = me.getValue(mp.get(bike, 'arrival_stations'))
        if mp.contains(arrival_stations, arrival_format):
            arrival_station = me.getValue(mp.get(arrival_stations, arrival_format))
            arrival_station[0] += 1
        else:
            mp.put(arrival_stations, arrival_format, [1])
        
    else:
        bike = mp.newMap(3, maptype='PROBING', loadfactor=0.5)
        bike_info = [1, int(trip['Trip  Duration'])]
        mp.put(bike, 'bike_info', bike_info)

        # Origin Stations Info
        origin_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(origin_stations, origin_format, [1])
        mp.put(bike, 'origin_stations', origin_stations)

        # Arrival Stations Info
        arrival_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(arrival_stations, arrival_format, [1])
        mp.put(bike, 'arrival_stations', arrival_stations)

        mp.put(analyzer['bikes_trips'], bike_id, bike)

def addConnections(analyzer):
    """
    Add the weigth (average duration) to each edge
    """
    origin_stations = mp.keySet(analyzer['stops'])
    for origin_station in lt.iterator(origin_stations):
        arrival_table = me.getValue(mp.get(analyzer['stops'], origin_station))
        arrival_stations = mp.keySet(arrival_table)
        for arrival_station in lt.iterator(arrival_stations):
            trip_info = me.getValue(mp.get(arrival_table, arrival_station))
            gr.addEdge(analyzer['connections'], origin_station, arrival_station, trip_info[0])

def addOutTripsMaxMin(analyzer):
    stations = mp.keySet(analyzer['out_stations'])
    total_trips = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

    for station in lt.iterator(stations):
        station_info = me.getValue(mp.get(analyzer['out_stations'], station))
        total_count = me.getValue(mp.get(station_info, 'total_count'))[0]

        trips_hour_map = me.getValue(mp.get(station_info, 'out_hours'))
        num_trips_hour = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)
        trips_hour = mp.keySet(trips_hour_map)

        for hour in lt.iterator(trips_hour):
            hour_info = me.getValue(mp.get(trips_hour_map, hour))
            if om.contains(num_trips_hour, hour_info[0]):
                hours_list = me.getValue(om.get(num_trips_hour, hour_info[0]))
                hours_list.append(hour)
            else:
                hours_list = []
                hours_list.append(hour)
                om.put(num_trips_hour, hour_info[0], hours_list)

        mp.put(station_info, 'num_trips_hour', num_trips_hour)

        trips_date_map = me.getValue(mp.get(station_info, 'num_trips'))
        num_trips_date = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)
        trips_date = mp.keySet(trips_date_map)

        for date in lt.iterator(trips_date):
            date_info = me.getValue(mp.get(trips_date_map, date))
            if om.contains(num_trips_date, date_info[0]):
                dates_list = me.getValue(om.get(num_trips_date, date_info[0]))
                dates_list.append(date)
            else:
                dates_list = []
                dates_list.append(date)
                om.put(num_trips_date, date_info[0], dates_list)

        mp.put(station_info, 'num_trips_date', num_trips_date)

        if om.contains(total_trips, total_count):
            stations_map = me.getValue(mp.get(total_trips, total_count))
            if mp.contains(stations_map, station):
                print('ERROR -------------------------------------------------------------------------------')
            else:
                mp.put(stations_map, station, station_info)
        else:
            stations_map = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
            mp.put(stations_map, station, station_info)
            om.put(total_trips, total_count, stations_map)

    analyzer['count_out_stations'] = total_trips


def addBikesMaxMin(analyzer):
    """
    Organize the stations of each bike by the number of trips
    """
    bikes = mp.keySet(analyzer['bikes_trips'])
    for bike in lt.iterator(bikes):
        bike_info = me.getValue(mp.get(analyzer['bikes_trips'], bike))

        # ORIGIN STATIONS

        origin_stations = mp.keySet(me.getValue(mp.get(bike_info, 'origin_stations')))

        origin_stations_map = me.getValue(mp.get(bike_info, 'origin_stations'))

        origin_stations_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for origin_station in lt.iterator(origin_stations):
            num_trips = me.getValue(mp.get(origin_stations_map, origin_station))
            num_trips = num_trips[0]
            if om.contains(origin_stations_num, num_trips):
                origin_stations_list = me.getValue(om.get(origin_stations_num, num_trips))
                if not lt.isPresent(origin_stations_list, origin_station):
                    lt.addLast(origin_stations_list, origin_station)

            else:
                origin_stations_list = lt.newList('ARRAY_LIST')
                lt.addLast(origin_stations_list, origin_station)
                om.put(origin_stations_num, num_trips, origin_stations_list)

        mp.put(bike_info, 'origin_stations_num', origin_stations_num)

        # ARRIVAL STATIONS

        arrival_stations = mp.keySet(me.getValue(mp.get(bike_info, 'arrival_stations')))

        arrival_stations_map = me.getValue(mp.get(bike_info, 'arrival_stations'))

        arrival_stations_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for arrival_station in lt.iterator(arrival_stations):
            num_trips = me.getValue(mp.get(arrival_stations_map, arrival_station))
            num_trips = num_trips[0]
            if om.contains(arrival_stations_num, num_trips):
                arrival_stations_list = me.getValue(om.get(arrival_stations_num, num_trips))
                if not lt.isPresent(arrival_stations_list, arrival_station):
                    lt.addLast(arrival_stations_list, arrival_station)

            else:
                arrival_stations_list = lt.newList('ARRAY_LIST')
                lt.addLast(arrival_stations_list, arrival_station)
                om.put(arrival_stations_num, num_trips, arrival_stations_list)

        mp.put(bike_info, 'arrival_stations_num', arrival_stations_num)

"""
def verticesList(analyzer):
    graph = analyzer['connections']
    list 
"""

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def requirement0(analyzer):
    graph = analyzer['connections']
    num_vertices = gr.numVertices(graph)
    num_edges = gr.numEdges(graph)

    return num_vertices, num_edges

def requirement1(analyzer):
    graph = analyzer['connections']
    out_stations = analyzer['count_out_stations']
    count_out_stations = om.keySet(analyzer['count_out_stations'])
    sorted_count_out_stations = sortList(count_out_stations, compareElements)
    first_five = lt.subList(sorted_count_out_stations, 1, 5)
    stations_list = lt.newList('ARRAY_LIST')
    for i in lt.iterator(first_five):
        station = me.getValue(om.get(out_stations, i))
        station_name = mp.keySet(station)
        for j in lt.iterator(station_name):
            info = me.getValue(mp.get(station, j))
            dates = me.getValue(mp.get(info, 'num_trips_date'))
            hours = me.getValue(mp.get(info, 'num_trips_hour'))
            max_hours = me.getValue(om.get(hours, om.maxKey(hours)))
            max_dates = me.getValue(om.get(dates, om.maxKey(dates)))
            tourist_count = me.getValue(mp.get(info, 'tourists_count'))[0]
            suscribers_count = me.getValue(mp.get(info, 'suscribers_count'))[0]
            total_count = me.getValue(mp.get(info, 'total_count'))[0]
            outdegree = gr.outdegree(graph, j)
            final_info = [j, [om.maxKey(hours), max_hours], [om.maxKey(dates), max_dates], tourist_count, suscribers_count, total_count, outdegree]
            lt.addLast(stations_list, final_info)
    return stations_list

def requirement3(analyzer):
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    num_elements = scc.connectedComponents(analyzer['components'])
    mapa_componentes_conectados = analyzer['components']['idscc'] 

    vertices = mp.keySet(mapa_componentes_conectados)

    tabla_hash_componentes = mp.newMap(num_elements, maptype="CHAINING", loadfactor=2, comparefunction=cmpcomponentes)

    for vertice in lt.iterator(vertices):
        num_componente = me.getValue(mp.get(mapa_componentes_conectados,vertice))

        if mp.contains(tabla_hash_componentes,num_componente):
            lt.addLast(me.getValue(mp.get(tabla_hash_componentes,num_componente)), vertice)

        else:
            lista_vertices = lt.newList()
            lt.addLast(lista_vertices, vertice)
            mp.put(tabla_hash_componentes,num_componente,lista_vertices)

    tabla_componentes = mp.newMap(num_elements, maptype="CHAINING", loadfactor=2, comparefunction=cmpcomponentes)

    for componente in lt.iterator(mp.keySet(tabla_hash_componentes)):
        vertices = me.getValue(mp.get(tabla_hash_componentes,componente))
        numero_estaciones = lt.size(vertices)
        max_viaje_inicio = 0
        max_viaje_final = 0
        vertice_inicio = ""
        vertice_final = ""
        for vertice in lt.iterator(vertices):
            grado_inicio = gr.outdegree(analyzer['connections'],vertice)
            grado_termina = gr.indegree(analyzer['connections'],vertice)

            if grado_inicio >= max_viaje_inicio:
                max_viaje_inicio = gr.outdegree(analyzer['connections'],vertice)
                vertice_inicio = vertice
            if grado_termina >= max_viaje_final:
                max_viaje_final = gr.indegree(analyzer['connections'],vertice)
                vertice_final = vertice

        mp.put(tabla_componentes, componente, (numero_estaciones, vertice_inicio, vertice_final))
            

    return tabla_componentes

def requirement4(analyzer, origin_station, arrival_station):
    origin_format = me.getValue(mp.get(analyzer['stations_formats'], origin_station))
    arrival_format = me.getValue(mp.get(analyzer['stations_formats'], arrival_station))
    minimumCostPaths(analyzer, origin_format)
    path = minimumCostPath(analyzer, arrival_format)
    list_path = lt.newList('ARRAY_LIST')
    time_count = 0
    while (not stack.isEmpty(path)):
        stop = stack.pop(path)
        station_info = (stop['weight'], stop['vertexA'])
        lt.addLast(list_path, station_info)
        time_count += stop['weight']
    arrival_id = me.getValue(mp.get(analyzer['stations_ids'], arrival_format))
    lt.addLast(list_path, (0, f'{arrival_id}-{arrival_station}'))
    return list_path, time_count

def requirement5(analyzer, initial_date, final_date):
    dates = analyzer['trips_dates']
    interval_dates = om.values(dates, initial_date, final_date)
    dates_info = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    total_trips = 0
    trips_duration = 0
    for i in lt.iterator(interval_dates):
        trip_info = me.getValue(mp.get(i, 'date_info'))
        total_trips += trip_info[0]
        trips_duration += trip_info[1]
        
        origin_stations = mp.keySet(me.getValue(mp.get(i, 'origin_stations')))
        origin_stations_map = me.getValue(mp.get(i, 'origin_stations'))
        origin_stations_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for origin_station in lt.iterator(origin_stations):
            num_trips = me.getValue(mp.get(origin_stations_map, origin_station))
            num_trips = num_trips[0]
            if om.contains(origin_stations_num, num_trips):
                origin_stations_list = me.getValue(om.get(origin_stations_num, num_trips))
                if not lt.isPresent(origin_stations_list, origin_station):
                    lt.addLast(origin_stations_list, origin_station)

            else:
                origin_stations_list = lt.newList('ARRAY_LIST')
                lt.addLast(origin_stations_list, origin_station)
                om.put(origin_stations_num, num_trips, origin_stations_list)

        arrival_stations = mp.keySet(me.getValue(mp.get(i, 'arrival_stations')))
        arrival_stations_map = me.getValue(mp.get(i, 'arrival_stations'))
        arrival_stations_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for arrival_station in lt.iterator(arrival_stations):
            num_trips = me.getValue(mp.get(arrival_stations_map, arrival_station))
            num_trips = num_trips[0]
            if om.contains(arrival_stations_num, num_trips):
                arrival_stations_list = me.getValue(om.get(arrival_stations_num, num_trips))
                if not lt.isPresent(arrival_stations_list, arrival_station):
                    lt.addLast(arrival_stations_list, arrival_station)

            else:
                arrival_stations_list = lt.newList('ARRAY_LIST')
                lt.addLast(arrival_stations_list, arrival_station)
                om.put(arrival_stations_num, num_trips, arrival_stations_list)

        initial_hours = mp.keySet(me.getValue(mp.get(i, 'initial_hours')))
        initial_hours_map = me.getValue(mp.get(i, 'initial_hours'))
        initial_hours_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for initial_hour in lt.iterator(initial_hours):
            num_trips = me.getValue(mp.get(initial_hours_map, initial_hour))
            num_trips = num_trips[0]
            if om.contains(initial_hours_num, num_trips):
                initial_hours_list = me.getValue(om.get(initial_hours_num, num_trips))
                if not lt.isPresent(initial_hours_list, initial_hour):
                    lt.addLast(initial_hours_list, initial_hour)

            else:
                initial_hours_list = lt.newList('ARRAY_LIST')
                lt.addLast(initial_hours_list, initial_hour)
                om.put(initial_hours_num, num_trips, initial_hours_list)

        finish_hours = mp.keySet(me.getValue(mp.get(i, 'finish_hours')))
        finish_hours_map = me.getValue(mp.get(i, 'finish_hours'))
        finish_hours_num = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for finish_hour in lt.iterator(finish_hours):
            num_trips = me.getValue(mp.get(finish_hours_map, finish_hour))
            num_trips = num_trips[0]
            if om.contains(finish_hours_num, num_trips):
                finish_hours_list = me.getValue(om.get(finish_hours_num, num_trips))
                if not lt.isPresent(finish_hours_list, finish_hour):
                    lt.addLast(finish_hours_list, finish_hour)

            else:
                finish_hours_list = lt.newList('ARRAY_LIST')
                lt.addLast(finish_hours_list, finish_hour)
                om.put(finish_hours_num, num_trips, finish_hours_list)

    mp.put(dates_info, 'finish_hours_num', finish_hours_num)
    mp.put(dates_info, 'initial_hours_num', initial_hours_num)
    mp.put(dates_info, 'arrival_stations_num', arrival_stations_num)
    mp.put(dates_info, 'origin_stations_num', origin_stations_num)

    origin_stations_order = me.getValue(mp.get(dates_info, 'origin_stations_num'))
    max_origin = om.maxKey(origin_stations_order)
    max_origin_stations = om.get(origin_stations_order, max_origin)

    arrival_stations_order = me.getValue(mp.get(dates_info, 'arrival_stations_num'))
    max_arrival = om.maxKey(arrival_stations_order)
    max_arrival_stations = om.get(arrival_stations_order, max_arrival)

    initial_hours_order = me.getValue(mp.get(dates_info, 'initial_hours_num'))
    max_initial = om.maxKey(initial_hours_order)
    max_initial_hours = om.get(initial_hours_order, max_initial)

    finish_hours_order = me.getValue(mp.get(dates_info, 'finish_hours_num'))
    max_finish = om.maxKey(finish_hours_order)
    max_finish_hours = om.get(finish_hours_order, max_finish)

    return max_origin_stations, max_arrival_stations, max_initial_hours, max_finish_hours, total_trips, trips_duration

def requirement6(analyzer, bike_id):
    bike = me.getValue(mp.get(analyzer['bikes_trips'], bike_id))
    bike_info = me.getValue(mp.get(bike, 'bike_info'))
    num_trips = bike_info[0]
    total_duration = bike_info[1]

    origin_stations = me.getValue(mp.get(bike, 'origin_stations_num'))
    max_origin = om.maxKey(origin_stations)
    max_origin_stations = om.get(origin_stations, max_origin)

    arrival_stations = me.getValue(mp.get(bike, 'arrival_stations_num'))
    max_arrival = om.maxKey(arrival_stations)
    max_arrival_stations = om.get(arrival_stations, max_arrival)

    return num_trips, total_duration, max_origin_stations, max_arrival_stations

# ==============================
# CMP FUNCTIONS
# ==============================

def cmp_grado_vertice(tupla1, tupla2):
    grado_vertice_1 = tupla1[1]
    grado_vertice_2 = tupla2[1]
    
    if grado_vertice_1 > grado_vertice_2:
        return True
    else:
        return False

def cmpTreeElements(element1, element2):
    if element1 == element2:
        return 0
    elif element1 > element2:
        return 1
    else:
        return -1

def compareDates(date1, date2):
    date_format1 = time.strptime(str(date1), "%m/%d/%Y")
    date_format2 = time.strptime(str(date2), "%m/%d/%Y")

    if (date_format1 == date_format2):
        return 0
    elif (date_format1 > date_format2):
        return 1
    else:
        return -1

def cmpcomponentes(numero1, numero2):

    if numero1 > me.getKey(numero2):
        return 1
    elif numero1 == me.getKey(numero2):
        return 0
    else:
        return -1

def compareElements(element1, element2):
    if element1 > element2:
        return True
    else:
        return False

# ==============================
# Funciones de consulta
# ==============================

def minimumCostPaths(analyzer, origin_format):
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], origin_format)

def minimumCostPath(analyzer, arrival_station):
    path = djk.pathTo(analyzer['paths'], arrival_station)
    return path

def sortList(list, cmp_function):
    return merge.sort(list, cmp_function)
