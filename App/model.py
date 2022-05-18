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
        'routes': None
    }

    analyzer['stops'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['routes'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
    analyzer['connections'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000)

    return analyzer

def addStopConnection(analyzer, trip):
    origin = trip['Start Station Name']
    destination = trip['End Station Name']
    addStop(analyzer, origin)
    addStop(analyzer, destination)
    addRoutes(analyzer, origin, destination, trip)
    

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
            addArrival(origin_station, destination, trip['Trip  Duration'])
        
    else:
        arrivals = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
        addArrival(arrivals, destination, trip['Trip  Duration'])
        mp.put(analyzer['stops'], origin, arrivals)

def addArrival(map, destination, trip_duration):
    trip_duration = int(trip_duration)
    durations = [trip_duration, trip_duration, 1]
    mp.put(map, destination, durations)

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