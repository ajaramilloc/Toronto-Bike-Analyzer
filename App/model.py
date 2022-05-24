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
        'bikes_trips': None
    }

    analyzer['stops'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['trip_routes'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['stations_ids'] = mp.newMap(790, maptype='PROBING', loadfactor=0.5)
    analyzer['bikes_trips'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000)

    return analyzer

def addStopConnection(analyzer, trip):
    origin = trip['Start Station Name']
    origin_filter = origin.split(' -')[0]
    arrival = trip['End Station Name']
    arrival_filter = arrival.split(' -')[0]
    addStop(analyzer, origin_filter)
    addStop(analyzer, arrival_filter)
    addRoutes(analyzer, origin_filter, arrival_filter, trip)
    addTrip(analyzer, trip)
    addStationId(analyzer, origin_filter, trip['Start Station Id'])
    addStationId(analyzer, arrival_filter, trip['End Station Id'])
    addBikeInfo(analyzer, trip['Bike Id'], trip, origin_filter, arrival_filter)

def addStop(analyzer, stop):
    if not gr.containsVertex(analyzer['connections'], stop):
        gr.insertVertex(analyzer['connections'], stop)

def addRoutes(analyzer, origin, destination, trip):
    if mp.contains(analyzer['stops'], origin):
        origin_station = me.getValue(mp.get(analyzer['stops'], origin))
        if mp.contains(origin_station, destination):
            arrival_station = me.getValue(mp.get(origin_station, destination))
            arrival_station[2] += 1
            arrival_station[1] += int(trip['Trip  Duration'])
            arrival_station[0] = arrival_station[1] / arrival_station[2]

        else:
            addArrival(origin_station, destination, trip['Trip  Duration'], trip['Trip Id'])
        
    else:
        arrivals = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
        addArrival(arrivals, destination, trip['Trip  Duration'], trip['Trip Id'])
        mp.put(analyzer['stops'], origin, arrivals)

def addArrival(map, destination, trip_duration, trip_id):
    trip_duration = int(trip_duration)
    trips_ids = lt.newList('ARRAY_LIST')
    lt.addLast(trips_ids, trip_id)
    durations = [trip_duration, trip_duration, 1, trips_ids]
    mp.put(map, destination, durations)

def addTrip(analyzer, trip):
    mp.put(analyzer['trip_routes'], trip['Trip Id'], trip)

def addStationId(analyzer, station, station_id):
    if mp.contains(analyzer['stations_ids'], station):
        pass
    else:
        mp.put(analyzer['stations_ids'], station, station_id)

def addBikeInfo(analyzer, bike_id, trip, origin, arrival):
    if mp.contains(analyzer['bikes_trips'], bike_id):
        bike = me.getValue(mp.get(analyzer['bikes_trips'], bike_id))

        bike_info = me.getValue(mp.get(bike, 'bike_info'))
        bike_info[0] += 1
        bike_info[1] += int(trip['Trip  Duration'])

        origin_stations = me.getValue(mp.get(bike, 'origin_stations'))
        if mp.contains(origin_stations, origin):
            origin_station = me.getValue(mp.get(origin_stations, origin))
            origin_station[0] += 1
        else:
            mp.put(origin_stations, origin, [1])

        arrival_stations = me.getValue(mp.get(bike, 'arrival_stations'))
        if mp.contains(arrival_stations, arrival):
            arrival_station = me.getValue(mp.get(arrival_stations, arrival))
            arrival_station[0] += 1
        else:
            mp.put(arrival_stations, arrival, [1])
        
    else:
        bike = mp.newMap(3, maptype='PROBING', loadfactor=0.5)
        bike_info = [1, int(trip['Trip  Duration'])]
        mp.put(bike, 'bike_info', bike_info)
        # Origin Stations Info
        origin_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(origin_stations, origin, [1])
        mp.put(bike, 'origin_stations', origin_stations)
        # Arrival Stations Info
        arrival_stations = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
        mp.put(arrival_stations, arrival, [1])
        mp.put(bike, 'arrival_stations', arrival_stations)

        mp.put(analyzer['bikes_trips'], bike_id, bike)

def addConnections(analyzer):
    origin_stations = mp.keySet(analyzer['stops'])
    for origin_station in lt.iterator(origin_stations):
        arrival_table = me.getValue(mp.get(analyzer['stops'], origin_station))
        arrival_stations = mp.keySet(arrival_table)
        for arrival_station in lt.iterator(arrival_stations):
            trip_info = me.getValue(mp.get(arrival_table, arrival_station))
            gr.addEdge(analyzer['connections'], origin_station, arrival_station, trip_info[0])

def addBikesMaxMin(analyzer):
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
    lista_vertices = gr.vertices(graph)
    lista_grados = lt.newList()
    for vertice in lt.iterator(lista_vertices):
        grado_vertice = gr.outdegree(graph, vertice)
        tupla_vertice = (vertice, grado_vertice)
        lt.addLast(lista_grados, tupla_vertice)

    sorted_list = merge.sort(lista_grados, cmp_grado_vertice)

    return sorted_list

def requirement3(analyzer):
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    num_elements = scc.connectedComponents(analyzer['components'])
    return num_elements

def requirement4(analyzer, origin_station, arrival_station):
    minimumCostPaths(analyzer, origin_station)
    path = minimumCostPath(analyzer, arrival_station)
    list_path = lt.newList('ARRAY_LIST')
    time_count = 0
    while (not stack.isEmpty(path)):
        stop = stack.pop(path)
        station_id = me.getValue(mp.get(analyzer['stations_ids'], stop['vertexA']))
        station_info = (stop['weight'], stop['vertexA'], station_id)
        lt.addLast(list_path, station_info)
        time_count += stop['weight']
    arrival_id = me.getValue(mp.get(analyzer['stations_ids'], arrival_station))
    lt.addLast(list_path, (0, arrival_station, arrival_id))
    return list_path, time_count

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

# ==============================
# Funciones de consulta
# ==============================

def minimumCostPaths(analyzer, origin_station):
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], origin_station)

def minimumCostPath(analyzer, arrival_station):
    path = djk.pathTo(analyzer['paths'], arrival_station)
    return path
