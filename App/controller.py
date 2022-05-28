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
 """

import config as cf
import model
import csv
import sys

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
    count_1 = 0
    count_2 = 0
    count_3 = 0
    count_4 = 0
    for trip in input_file:
        # Data Filter
        
        
        if trip['Trip  Duration'] == '0':
            count_1 += 1
        if (trip['Trip  Duration'] == '') or (trip['Start Station Id'] == '') or (trip['End Station Id'] == '') or (trip['Bike Id'] == ''):
            count_3 += 1
        if trip['Start Station Name'] == trip['End Station Name']:
                count_4 += 1
        if (trip['Trip  Duration'] == '') or (trip['Start Station Id'] == '') or (trip['End Station Id'] == '') or (trip['Trip  Duration'] == '0') or (trip['Bike Id'] == ''):
            pass
        else:
            # Add Station Info
            model.addStopConnection(analyzer, trip)
            count_2 += 1
    # Add edges weights
    model.addConnections(analyzer)
    # Organize the bikes info
    model.addBikesMaxMin(analyzer)

    model.addOutTripsMaxMin(analyzer)
    
    return(count_1, count_2, count_3, count_4)

# -----------------------------------------------------
# REQUIREMENTS FUNCTIONS
# -----------------------------------------------------

def requirement0(analyzer):
    return model.requirement0(analyzer)

def requirement1(analyzer):
    return model.requirement1(analyzer)

def requirement3(analyzer):
    return model.requirement3(analyzer)

def requirement4(analyzer, origin_station, arrival_station):
    return model.requirement4(analyzer, origin_station, arrival_station)

def requirement5(analyzer, initial_date, final_date):
    return model.requirement5(analyzer, initial_date, final_date)

def requirement6(analyzer, bike_id):
    return model.requirement6(analyzer, bike_id)
    
    
