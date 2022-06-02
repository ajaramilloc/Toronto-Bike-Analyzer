import config as cf
from DISClib.ADT import graph as gr
from DISClib.ADT import stack
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import prim
from DISClib.Algorithms.Graphs import dfs
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.Algorithms.Sorting import mergesort as merge
import time
import math
assert cf

# -----------------------------------------------------
# NEW ANALYZER
# -----------------------------------------------------

def newAnalyzer():
    
    analyzer = {
        'connections_digraph': None,
        'connections_graph': None,
        'stations_format_map': None,
        'stations_info': None,
        'routes_average_map': None,
        'bikes_trips_map': None,
        'out_trips_tree': None,
        'date_out_trips_tree': None,
        'date_in_trips_tree': None,
        'dates_tree': None
        
    }

    analyzer['connections_digraph'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000) # digraph
    analyzer['connections_graph'] = gr.newGraph(datastructure='ADJ_LIST', directed=False, size=36000) # graph
    analyzer['stations_format_map'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['stations_info'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['routes_average_map'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['bikes_trips_map'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # map
    analyzer['out_trips_map'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # map
    analyzer['date_out_trips_tree'] = om.newMap(omaptype='RBT', comparefunction=compareDates) # tree
    analyzer['date_in_trips_tree'] = om.newMap(omaptype='RBT', comparefunction=compareDates) # tree
    analyzer['dates_tree'] = om.newMap(omaptype='RBT', comparefunction=compareDates) # tree

    return analyzer

def addStop(analyzer, trip):
    """
    Add the stations info in all the structures
    """
    # Format origin station
    if trip['Start Station Name'] == '':
        trip['Start Station Name'] = 'UNKNOWN'
    origin_format = formatStation(trip['Start Station Id'], trip['Start Station Name'])

    # Format arrival station    
    if trip['End Station Name'] == '':
        trip['End Station Name'] = 'UNKNOWN'
    arrival_format = formatStation(trip['End Station Id'], trip['End Station Name'])

    # Format trips dates
    init_trip_date_time = trip['Start Time']
    finish_trip_date_time = trip['End Time']
    init_trip_date = formatDateTime(trip['Start Time'])[0]
    init_trip_hour = formatDateTime(trip['Start Time'])[1]
    finish_trip_date = formatDateTime(trip['End Time'])[0]
    finish_trip_hour = formatDateTime(trip['End Time'])[1]

    # Add station to the digraph
    addStationDigraph(analyzer, origin_format)
    addStationDigraph(analyzer, arrival_format)

    # Add station to the graph
    addStationGraph(analyzer, origin_format)
    addStationGraph(analyzer, arrival_format)

    # Add station format in station names map

    addStationFormat(analyzer, trip['Start Station Name'], origin_format)
    addStationFormat(analyzer, trip['End Station Name'], arrival_format)

    # Calculates route average

    addRoutesAverage(analyzer, origin_format, arrival_format, trip)

    # Add out trip info

    addOutTrips(analyzer, origin_format, init_trip_date, init_trip_hour, trip)

    if trip['User Type'] == 'Annual Member':
        # Add out trip info by date

        addTripsByDate(analyzer['date_out_trips_tree'], origin_format, init_trip_date, init_trip_hour)

        # Add in trip info by date

        addTripsByDate(analyzer['date_in_trips_tree'], arrival_format, finish_trip_date, finish_trip_hour)

        # Add trip date

        addDateCount(analyzer, init_trip_date, finish_trip_date, trip)

    # Add bike info

    addBikeInfo(analyzer, int(float(trip['Bike Id'])), trip, origin_format, arrival_format)

    #addStationInfo(analyzer, )

# -----------------------------------------------------
# ADD INFO FUNCTIONS
# -----------------------------------------------------

    
def addStationDigraph(analyzer, station_format):
    """
    Add a vertex to the digraph
    """
    if not gr.containsVertex(analyzer['connections_digraph'], station_format):
        gr.insertVertex(analyzer['connections_digraph'], station_format)

def addStationGraph(analyzer, station_format):
    """
    Add a vertex to the graph
    """
    if not gr.containsVertex(analyzer['connections_graph'], station_format):
        gr.insertVertex(analyzer['connections_graph'], station_format)

def addStationFormat(analyzer, station_name, station_format):
    """
    Add the station format in the stations name map key->station_name / value->station_format
    """
    if not mp.contains(analyzer['stations_format_map'], station_name):
        mp.put(analyzer['stations_format_map'], station_name, station_format)

def addDateCount(analyzer, init_trip_date, finish_trip_date, trip):
    # ----------------------------------------------------------------------------------------------- #
    def addDateInfoTree(tree, date, trip):
        if om.contains(tree, date):
            date_info = me.getValue(mp.get(tree, date))

            time_count = me.getValue(mp.get(date_info, 'time_count'))
            time_count[0] += int(trip['Trip  Duration'])

            trips_count = me.getValue(mp.get(date_info, 'trips_count'))
            trips_count[0] += 1
        else:
            date_info = mp.newMap(4, maptype='PROBING', loadfactor=0.5)
            time_count = [int(trip['Trip  Duration'])]
            trips_count = [1]

            mp.put(date_info, 'time_count', time_count)
            mp.put(date_info, 'trips_count', trips_count)

            om.put(tree, date, date_info)
    # ----------------------------------------------------------------------------------------------- #
    if init_trip_date == finish_trip_date:
        addDateInfoTree(analyzer['dates_tree'], init_trip_date, trip)
    else:
        addDateInfoTree(analyzer['dates_tree'], finish_trip_date, trip)

def addRoutesAverage(analyzer, origin_format, arrival_format, trip):
    """
    For each trip calculates and add the average duration
    """

    # ----------------------------------------------------------------------------------------------- #
    def addArrival(map, arrival_format, trip_duration):
        """
        Add a list to the trip, pos 0: Average / pos 1: Durations sum / pos 2: Total trips
        """
        trip_duration = int(trip_duration)
        durations = [trip_duration, trip_duration, 1]
        mp.put(map, arrival_format, durations)
    # ----------------------------------------------------------------------------------------------- #

    if mp.contains(analyzer['routes_average_map'], origin_format):
        arrivals = me.getValue(mp.get(analyzer['routes_average_map'], origin_format))
        if mp.contains(arrivals, arrival_format):
            arrival_info = me.getValue(mp.get(arrivals, arrival_format))
            arrival_info[2] += 1
            arrival_info[1] += int(trip['Trip  Duration'])
            arrival_info[0] = arrival_info[1] / arrival_info[2]

        else:
            addArrival(arrivals, arrival_format, trip['Trip  Duration'])
        
    else:
        arrivals = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
        addArrival(arrivals, arrival_format, trip['Trip  Duration'])
        mp.put(analyzer['routes_average_map'], origin_format, arrivals)

def addOutTrips(analyzer, origin_format, trip_date, init_trip_hour, trip):
    if mp.contains(analyzer['out_trips_map'], origin_format):
        station_info = me.getValue(mp.get(analyzer['out_trips_map'], origin_format))

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

        out_hours = mp.newMap(24, maptype='PROBING', loadfactor=0.5)
        mp.put(out_hours, hour_format, [1])
        mp.put(station_info, 'out_hours', out_hours)

        num_trips = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        mp.put(num_trips, trip_date, [1])
        mp.put(station_info, 'num_trips', num_trips)

        mp.put(analyzer['out_trips_map'], origin_format, station_info)

def addTripsByDate(tree, station_format, trip_date, trip_hour):
    if om.contains(tree, trip_date):
        date_info = me.getValue(mp.get(tree, trip_date))

        hours = me.getValue(mp.get(date_info, 'hours'))
        format = trip_hour.split(':')[0]
        hour_format = f'{format}:00 - {format}:59'
        if mp.contains(hours, hour_format):
            hour = me.getValue(mp.get(hours, hour_format))
            hour[0] += 1
        else:
            mp.put(hours, hour_format, [1])

        stations = me.getValue(mp.get(date_info, 'stations'))
        if mp.contains(stations, station_format):
            station = me.getValue(mp.get(stations, station_format))
            station[0] += 1
        else:
            mp.put(stations, station_format, [1])

    else:
        date_info = mp.newMap(4, maptype='PROBING', loadfactor=0.5)

        format = trip_hour.split(':')[0]
        hour_format = f'{format}:00 - {format}:59'

        hours = mp.newMap(24, maptype='PROBING', loadfactor=0.5)
        mp.put(hours, hour_format, [1])
        mp.put(date_info, 'hours', hours)

        stations = mp.newMap(1, maptype='PROBING', loadfactor=0.5)
        mp.put(stations, station_format, [1])
        mp.put(date_info, 'stations', stations)

        om.put(tree, trip_date, date_info)
 

def addBikeInfo(analyzer, bike_id, trip, origin_format, arrival_format):
    """
    - Add the bike id in the map bikes_trips
    - Add the total trips and total duration with the bike
    - Add the origin and arrival stations of the bike
    - Each station have the total trips
    """
    if mp.contains(analyzer['bikes_trips_map'], bike_id):
        bike = me.getValue(mp.get(analyzer['bikes_trips_map'], bike_id))

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

        mp.put(analyzer['bikes_trips_map'], bike_id, bike)

def addTripsByDateTime(analyzer, station_format, trip_date_time):
    if mp.contains(analyzer['stations_info'], station_format):
        pass
    else:
        station_info = mp.newMap(3, maptype='PROBING')
# -----------------------------------------------------
# UNIFY FUNCTIONS
# -----------------------------------------------------
    
def addConnectionsDigraph(analyzer):
    """
    Add the weigth (average duration) to each edge
    """
    origin_stations = mp.keySet(analyzer['routes_average_map'])
    for origin_station in lt.iterator(origin_stations):
        arrival_table = me.getValue(mp.get(analyzer['routes_average_map'], origin_station))
        arrival_stations = mp.keySet(arrival_table)
        for arrival_station in lt.iterator(arrival_stations):
            trip_info = me.getValue(mp.get(arrival_table, arrival_station))
            gr.addEdge(analyzer['connections_digraph'], origin_station, arrival_station, trip_info[0])

def addConnectionsGraph(analyzer):
    """
    Add the weigth (average duration) to each edge
    """
    origin_stations = mp.keySet(analyzer['routes_average_map'])
    for origin_station in lt.iterator(origin_stations):
        arrival_table = me.getValue(mp.get(analyzer['routes_average_map'], origin_station))
        arrival_stations = mp.keySet(arrival_table)
        for arrival_station in lt.iterator(arrival_stations):
            tripA = getEdge(analyzer['connections_digraph'], origin_station, arrival_station)
            tripB = getEdge(analyzer['connections_digraph'], arrival_station, origin_station)
            if tripA != None and tripB != None:
                if tripA['weight'] > tripB['weight']:
                    gr.addEdge(analyzer['connections_graph'], origin_station, arrival_station, tripA['weight'])
                elif tripA['weight'] < tripB['weight']:
                    gr.addEdge(analyzer['connections_graph'], origin_station, arrival_station, tripB['weight'])
                elif tripA['weight'] == tripB['weight']:
                    gr.addEdge(analyzer['connections_graph'], origin_station, arrival_station, tripA['weight'])

def unifyOutTrips(analyzer):
    stations = mp.keySet(analyzer['out_trips_map'])
    total_trips = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

    for station in lt.iterator(stations):
        station_info = me.getValue(mp.get(analyzer['out_trips_map'], station))
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

    analyzer['out_trips_tree'] = total_trips

def unifyBikesInfo(analyzer):
    """
    Organize the stations of each bike by the number of trips
    """
    bikes = mp.keySet(analyzer['bikes_trips_map'])
    for bike in lt.iterator(bikes):
        bike_info = me.getValue(mp.get(analyzer['bikes_trips_map'], bike))

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
# GENERIC FUNCTIONS
# -----------------------------------------------------

def formatStation(station_id, station_name):
    format_id = station_id.split('.')[0]
    station_format = f'{format_id}-{station_name}'
    return station_format

def formatDateTime(trip_date_time):
    trip_date = trip_date_time.split(' ')[0]
    trip_hour = trip_date_time.split(' ')[1]
    return trip_date, trip_hour

def getEdge(graph, vertexA, vertexB):
    try:
        edge = gr.getEdge(graph, vertexA, vertexB)
        return edge
    except Exception:
        return None

def sortList(list, cmp_function):
    return merge.sort(list, cmp_function)

# -----------------------------------------------------
# CMP FUNCTIONS
# -----------------------------------------------------

def cmpTreeElements(element1, element2):
    if element1 == element2:
        return 0
    elif element1 > element2:
        return 1
    else:
        return -1

def compareElements(element1, element2):
    if element1 > element2:
        return True
    else:
        return False

def cmp_grado_componente(componente1, componente2):
    grado_componente1 = componente1[0]
    grado_componente2 = componente2[0]

    if grado_componente1 > grado_componente2:
        return True
    else:
        return False

def cmpcomponentes(numero1, numero2):

    if numero1 > me.getKey(numero2):
        return 1
    elif numero1 == me.getKey(numero2):
        return 0
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

def compareDatesTime(date1, date2):
    date_format1 = time.strptime(str(date1), "%m/%d/%Y %H:%M")
    date_format2 = time.strptime(str(date2), "%m/%d/%Y %H:%M")

    if (date_format1 == date_format2):
        return 0
    elif (date_format1 > date_format2):
        return 1
    else:
        return -1

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def charge(analyzer):
    vertices = gr.vertices(analyzer['connections_digraph'])
    size = lt.size(vertices)
    first_3 = lt.subList(vertices, 1, 3)
    last_3 = lt.subList(vertices, size-3, 3)
    total_vertices = lt.newList('ARRAY_LIST')
    for first_station in lt.iterator(first_3):
        station_id = first_station
        station_name = first_station
        print(first_station)
        try:
            station_indegree = gr.indegree(analyzer['connections_digraph'], first_station)
            station_outdegree = gr.outdegree(analyzer['connections_digraph'], first_station)
        except Exception:
            station_indegree = 0
            station_outdegree = 0
            print(first_station)

        format_first_station = {'station_id': station_id, 'station_name': station_name, 'indegree': station_indegree, 'outdegree': station_outdegree}
        lt.addLast(total_vertices, format_first_station)

    for last_station in lt.iterator(last_3):
        station_id = last_station
        station_name = last_station
        try:
            station_indegree = gr.indegree(analyzer['connections_digraph'], last_station)
            station_outdegree = gr.outdegree(analyzer['connections_digraph'], last_station)
        except Exception:
            station_indegree = 0
            station_outdegree = 0
        format_first_station = {'station_id': station_id, 'station_name': station_name, 'indegree': station_indegree, 'outdegree': station_outdegree}
        lt.addLast(total_vertices, format_first_station)
    
    digraph = analyzer['connections_digraph']
    num_vertices_digraph = gr.numVertices(digraph)
    num_edges_digraph = gr.numEdges(digraph)

    graph = analyzer['connections_graph']
    num_vertices_graph = gr.numVertices(graph)
    num_edges_graph = gr.numEdges(graph)

    return num_vertices_digraph, num_edges_digraph, num_vertices_graph, num_edges_graph, total_vertices

def requirement1(analyzer):
    graph = analyzer['connections_digraph']
    out_stations = analyzer['out_trips_tree']
    count_out_stations = om.keySet(analyzer['out_trips_tree'])
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
    first_five_stations = lt.subList(stations_list, 1, 5)
    return first_five_stations

def requirement2(analyzer, origin_station, max_time, min_stations, max_routes):
    origin_format = me.getValue(mp.get(analyzer['stations_format_map'], origin_station))
    dijkstra = djk.Dijkstra(analyzer['connections_digraph'], origin_format)
    stations = mp.keySet(dijkstra['visited'])
    max_one_trip_duration = max_time / 2
    routes_list_distance = lt.newList('ARRAY_LIST')
    routes_list = lt.newList('ARRAY_LIST')
    for station in lt.iterator(stations):
        distance = djk.distTo(dijkstra, station)
        if distance != math.inf and distance <= max_one_trip_duration:
            posible_route = djk.pathTo(dijkstra, station)
            lt.addLast(routes_list_distance, posible_route)

    for stop in lt.iterator(routes_list_distance):
        route_size = stack.size(stop)
        if route_size >= min_stations:
            lt.addLast(routes_list, stop)
            
    user_routes = lt.subList(routes_list, 1, max_routes)

    list_paths = lt.newList('ARRAY_LIST')
    for route in lt.iterator(user_routes):
        list_path = lt.newList('ARRAY_LIST')
        time_count = 0
        while (not stack.isEmpty(route)):
            stop = stack.pop(route)
            station_info = (stop['weight'], stop['vertexA'], stop['vertexB'])
            lt.addLast(list_path, station_info)
            time_count += stop['weight']
        path_info = [time_count, list_path]
        lt.addLast(list_paths, path_info)
    return lt.size(routes_list), list_paths

def requirement3(analyzer):
    analyzer['components'] = scc.KosarajuSCC(analyzer['connections_digraph'])
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
            grado_inicio = gr.outdegree(analyzer['connections_digraph'],vertice)
            grado_termina = gr.indegree(analyzer['connections_digraph'],vertice)

            if grado_inicio >= max_viaje_inicio:
                max_viaje_inicio = gr.outdegree(analyzer['connections_digraph'],vertice)
                vertice_inicio = vertice
            if grado_termina >= max_viaje_final:
                max_viaje_final = gr.indegree(analyzer['connections_digraph'],vertice)
                vertice_final = vertice

        mp.put(tabla_componentes, componente, (numero_estaciones, vertice_inicio, vertice_final))
            
    lista_componentes = lt.newList()

    for componente in lt.iterator(mp.keySet(tabla_componentes)):
        lt.addLast(lista_componentes, me.getValue(mp.get(tabla_componentes,componente)))

    lista_sorteada = sortList(lista_componentes, cmp_grado_componente)
    return lista_sorteada

def requirement4(analyzer, origin_station, arrival_station):
    # -------------------------------------------------------------------------------------- #
    def minimumCostPaths(analyzer, origin_format):
        analyzer['paths'] = djk.Dijkstra(analyzer['connections_digraph'], origin_format)

    def minimumCostPath(analyzer, arrival_station):
        path = djk.pathTo(analyzer['paths'], arrival_station)
        return path
    # -------------------------------------------------------------------------------------- #
    
    origin_format = me.getValue(mp.get(analyzer['stations_format_map'], origin_station))
    arrival_format = me.getValue(mp.get(analyzer['stations_format_map'], arrival_station))

    minimumCostPaths(analyzer, origin_format)
    path = minimumCostPath(analyzer, arrival_format)
    list_path = lt.newList('ARRAY_LIST')
    time_count = 0
    while (not stack.isEmpty(path)):
        stop = stack.pop(path)
        station_info = (stop['weight'], stop['vertexA'])
        lt.addLast(list_path, station_info)
        time_count += stop['weight']
    lt.addLast(list_path, (0, f'{arrival_format}'))
    return list_path, time_count

def requirement5(analyzer, init_date, finish_date):
    # -------------------------------------------------------------------------------------- #
    def unifyDatesInterval(tree, init_date, finish_date):
        dates_interval = om.values(tree, init_date, finish_date)
        interval = mp.newMap(2, maptype='PROBING', loadfactor=0.5)
        total_stations = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        total_hours = mp.newMap(15, maptype='PROBING', loadfactor=0.5)
        for date in lt.iterator(dates_interval):
            hours = mp.keySet(me.getValue(mp.get(date, 'hours')))
            hours_map = me.getValue(mp.get(date, 'hours'))
            for hour in lt.iterator(hours):
                num_trips = me.getValue(mp.get(hours_map, hour))
                num_trips = num_trips[0]
                if mp.contains(total_hours, hour):
                    hour_info = me.getValue(mp.get(total_hours, hour))
                    hour_info[0] += num_trips
                else:
                    mp.put(total_hours, hour, [num_trips])

            stations = mp.keySet(me.getValue(mp.get(date, 'stations')))
            stations_map = me.getValue(mp.get(date, 'stations'))
            for station in lt.iterator(stations):
                num_trips = me.getValue(mp.get(stations_map, station))
                num_trips = num_trips[0]
                if mp.contains(total_stations, station):
                    station_info = me.getValue(mp.get(total_stations, station))
                    station_info[0] += num_trips
                else:
                    mp.put(total_stations, station, [num_trips])

        mp.put(interval, 'total_stations', total_stations)
        mp.put(interval, 'total_hours', total_hours)

        return interval
    # -------------------------------------------------------------------------------------- #
    def organizeDatesInterval(map, property):
        property_map = me.getValue(mp.get(map, f'{property}'))
        property_key_set = mp.keySet(property_map)
        property_tree = om.newMap(omaptype='RBT', comparefunction=cmpTreeElements)

        for element in lt.iterator(property_key_set):
            property_count = me.getValue(mp.get(property_map, element))
            property_count = property_count[0]
            if om.contains(property_tree, property_count):
                property_list = me.getValue(mp.get(property_tree, property_count))
                lt.addLast(property_list, element)
            else:
                property_list = lt.newList('ARRAY_LIST')
                lt.addLast(property_list, element)
                om.put(property_tree, property_count, property_list)

        return property_tree
    # -------------------------------------------------------------------------------------- #
    interval_dates = om.values(analyzer['dates_tree'], init_date, finish_date)
    total_time = 0
    total_trips = 0
    for date in lt.iterator(interval_dates):
        time_count = me.getValue(mp.get(date, 'time_count'))[0]
        total_time += time_count
        trips_count = me.getValue(mp.get(date, 'trips_count'))[0]
        total_trips += trips_count

    out_dates = analyzer['date_out_trips_tree']
    out_dates_interval = unifyDatesInterval(out_dates, init_date, finish_date)

    out_dates_total_hours_tree = organizeDatesInterval(out_dates_interval, 'total_hours')
    max_out_hours = om.maxKey(out_dates_total_hours_tree)
    max_out_hours_info = me.getValue(om.get(out_dates_total_hours_tree, max_out_hours))
    out_dates_total_stations_tree = organizeDatesInterval(out_dates_interval, 'total_stations')
    max_out_stations = om.maxKey(out_dates_total_stations_tree)
    max_out_stations_info = me.getValue(om.get(out_dates_total_stations_tree, max_out_stations))

    in_dates = analyzer['date_in_trips_tree']
    in_dates_interval = unifyDatesInterval(in_dates, init_date, finish_date)

    in_dates_total_hours_tree = organizeDatesInterval(in_dates_interval, 'total_hours')
    max_in_hours = om.maxKey(in_dates_total_hours_tree)
    max_in_hours_info = me.getValue(om.get(in_dates_total_hours_tree, max_in_hours))
    in_dates_total_stations_tree = organizeDatesInterval(in_dates_interval, 'total_stations')
    max_in_stations = om.maxKey(in_dates_total_stations_tree)
    max_in_stations_info = me.getValue(om.get(in_dates_total_stations_tree, max_in_stations))

    return [max_out_hours, max_out_hours_info], [max_out_stations, max_out_stations_info], [max_in_hours, max_in_hours_info], [max_in_stations, max_in_stations_info], total_time, total_trips

def requirement6(analyzer, bike_id):
    bike = me.getValue(mp.get(analyzer['bikes_trips_map'], bike_id))
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