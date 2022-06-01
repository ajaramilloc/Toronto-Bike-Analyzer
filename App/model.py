import config as cf
from DISClib.ADT import graph as gr
from DISClib.ADT import stack
from DISClib.Algorithms.Graphs import scc
from DISClib.Algorithms.Graphs import dijsktra as djk
from DISClib.Algorithms.Graphs import dfs
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
        'connections_digraph': None,
        'connections_graph': None,
        'stations_format_map': None,
        'stations_info': None,
        'routes_average_map': None,
        'bikes_trips_map': None,
        'out_stations': None,
        'out_trips_tree': None
        
    }

    analyzer['connections_digraph'] = gr.newGraph(datastructure='ADJ_LIST', directed=True, size=36000) # digraph
    analyzer['connections_graph'] = gr.newGraph(datastructure='ADJ_LIST', directed=False, size=36000) # graph
    analyzer['stations_format_map'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['stations_info'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['routes_average_map'] = mp.newMap(708, maptype='PROBING', loadfactor=0.5) # map
    analyzer['bikes_trips_map'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # map
    analyzer['out_stations'] = mp.newMap(15, maptype='PROBING', loadfactor=0.5) # map

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
    trip_date = formatDateTime(trip['Start Time'])[0]
    init_trip_hour = formatDateTime(trip['Start Time'])[1]
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

    addOutTrips(analyzer, origin_format, trip_date, init_trip_hour, trip)

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
    station_format = f'{int(float(station_id))}-{station_name}'
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

def minimumCostPaths(analyzer, origin_format):
    analyzer['paths'] = djk.Dijkstra(analyzer['connections_digraph'], origin_format)

def minimumCostPath(analyzer, arrival_station):
    path = djk.pathTo(analyzer['paths'], arrival_station)
    return path

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

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def charge(analyzer):
    digraph = analyzer['connections_digraph']
    num_vertices_digraph = gr.numVertices(digraph)
    num_edges_digraph = gr.numEdges(digraph)

    graph = analyzer['connections_graph']
    num_vertices_graph = gr.numVertices(graph)
    num_edges_graph = gr.numEdges(graph)

    return num_vertices_digraph, num_edges_digraph, num_vertices_graph, num_edges_graph

def requirement1(analyzer):
    graph = analyzer['connections_digraph']
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

def requirement4(analyzer, origin_station, arrival_station):
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

