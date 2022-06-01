import config as cf
import model
import csv
import sys
from DISClib.ADT import list as lt

default_limit = 1000
sys.setrecursionlimit(default_limit*10)
csv.field_size_limit(2147483647)

# -----------------------------------------------------
# NEW CONTROLLER
# -----------------------------------------------------

def newController():
    analyzer = model.newAnalyzer()
    return analyzer

# -----------------------------------------------------
# LOADING DATA FUNCTIONS
# -----------------------------------------------------

def loadData(analyzer):
    trips_file = cf.data_dir + 'Bikeshare/Bikeshare-ridership-2021-utf8-small.csv'
    input_file = csv.DictReader(open(trips_file, encoding='utf-8'))
    trips = lt.newList('ARRAY_LIST')
    count_1 = 0
    count_2 = 0
    count_3 = 0
    count_4 = 0
    count_5 = 0
    for trip in input_file:
        # Data Filter
        if trip['Trip  Duration'] == '0':
            count_1 += 1
        if (trip['Trip  Duration'] == '') or (trip['Start Station Id'] == '') or (trip['End Station Id'] == '') or (trip['Bike Id'] == ''):
            count_3 += 1
        if trip['Start Station Name'] == trip['End Station Name']:
            count_4 += 1
        if (trip['Trip  Duration'] == '') or (trip['Start Station Id'] == '') or (trip['End Station Id'] == '') or (trip['Trip  Duration'] == '0') or (trip['Bike Id'] == ''): #or (trip['Start Station Name'] == trip['End Station Name']):
            count_5 += 1
            pass
        else:
            # Add Station Info
            model.addStop(analyzer, trip)
            count_2 += 1
            lt.addLast(trips, trip)
    # Add edges weights
    model.addConnectionsDigraph(analyzer)
    model.addConnectionsGraph(analyzer)
    # Unify out trips
    model.unifyOutTrips(analyzer)
    # Unify bikes info
    model.unifyBikesInfo(analyzer)
    
    return(count_1, count_2, count_3, count_4, count_5, trips)

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def charge(analyzer):
    return model.charge(analyzer)

def requirement1(analyzer):
    return model.requirement1(analyzer)

def requirement4(analyzer, origin_station, arrival_station):
    return model.requirement4(analyzer, origin_station, arrival_station)

def requirement6(analyzer, bike_id):
    return model.requirement6(analyzer, bike_id)