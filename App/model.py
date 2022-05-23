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
        'stations_ids': None
    }

    analyzer['stops'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['trip_routes'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['stations_ids'] = mp.newMap(790, maptype='PROBING', loadfactor=0.5)
    analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000)

    return analyzer

def addStopConnection(analyzer, trip):
    origin = trip['Start Station Name']
    origin_filter = origin.split(' -')[0]
    destination = trip['End Station Name']
    destination_filter = destination.split(' -')[0]
    addStop(analyzer, origin_filter)
    addStop(analyzer, destination_filter)
    addRoutes(analyzer, origin_filter, destination_filter, trip)
    addTrip(analyzer, trip)
    addStationId(analyzer, origin_filter, trip['Start Station Id'])
    addStationId(analyzer, destination_filter, trip['End Station Id'])

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

def addConnections(analyzer):
    origin_stations = mp.keySet(analyzer['stops'])
    for origin_station in lt.iterator(origin_stations):
        arrival_table = me.getValue(mp.get(analyzer['stops'], origin_station))
        arrival_stations = mp.keySet(arrival_table)
        for arrival_station in lt.iterator(arrival_stations):
            trip_info = me.getValue(mp.get(arrival_table, arrival_station))
            gr.addEdge(analyzer['connections'], origin_station, arrival_station, trip_info[0])

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def requirement0(analyzer):
    graph = analyzer['connections']
    num_vertices = gr.numVertices(graph)
    num_edges = gr.numEdges(graph)

    return num_vertices, num_edges

def requirement3(analyzer):
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections'])
    num_elements = scc.connectedComponents(analyzer['components'])
    return num_elements

def requirement4(analyzer, origin_station, arrival_station):
    minimumCostPaths(analyzer, origin_station)
    path = minimumCostPath(analyzer, arrival_station)
    while (not stack.isEmpty(path)):
        stop = stack.pop(path)
        print(stop)
    return path

# ==============================
# Funciones de consulta
# ==============================

def minimumCostPaths(analyzer, origin_station):
    analyzer['paths'] = djk.Dijkstra(analyzer['connections'], origin_station)

def minimumCostPath(analyzer, arrival_station):
    path = djk.pathTo(analyzer['paths'], arrival_station)
    return path
