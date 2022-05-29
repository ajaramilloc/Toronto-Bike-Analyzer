"""
 * Copyright 2020, Departamento de sistemas y Computación, Universidad
 * de Los Andes
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
import sys
import controller
from DISClib.ADT import list as lt
from DISClib.ADT import map as mp
from DISClib.DataStructures import mapentry as me
from DISClib.ADT import orderedmap as om
from DISClib.ADT import graph as gr
assert cf
import time

# -----------------------------------------------------
# NEW CONTROLLER
# -----------------------------------------------------

def newController():
    control = controller.newController()
    return control

def printMenu():
    print("Bienvenido")
    print("0- Cargar información en el catálogo")
    print("1- Comprar bicicletas para las estaciones con más viajes de origen")
    print("2- Planear paseos turísticos por la ciudad")
    print("3- Reconocer los componentes fuertemente conectados")
    print("4- Planear una ruta rápida para el usuario")
    print("5- Reportar rutas en un rango de fechas para los usuarios anuales")
    print("6- Planear el mantenimiento preventivo de bicicleta")
    print("7- La estación más frecuentada por los visitantes")

# -----------------------------------------------------
# GENERIC FUNCTIONS
# -----------------------------------------------------

def getTime():
    """
    devuelve el instante tiempo de procesamiento en milisegundos
    """
    return float(time.perf_counter()*1000)


def deltaTime(end, start):
    """
    devuelve la diferencia entre tiempos de procesamiento muestreados
    """
    elapsed = float(end - start)
    return elapsed

# -----------------------------------------------------
# PRINT FUNCTIONS
# -----------------------------------------------------

def optionOne(control):
    respuesta = controller.requirement1(control)
    for i in lt.iterator(respuesta):
        station_id = i[0].split('-')[0]
        station_name = i[0].split('-')[1]
        outdegree = i[6]
        suscribers_count = i[4]
        tourist_count = i[3]
        total_count = i[5]
        hours = i[1]
        dates = i[2]
        print(f'id -> {station_id} | name -> {station_name} | out trips -> {total_count} | suscribers trips -> {suscribers_count} | tourist trips -> {tourist_count} |  outdegree -> {outdegree} | rush hour -> {hours[0], hours[1][0]} | rush date -> {dates[0], dates[1][0]}')

def optionTwo(control):
    station_name = input('Enter the origin station: ') #Roxborough St W / Yonge St
    min_stations = int(input('Enter the min number of stations: ')) #5
    max_time = int(input('Enter the max time: ')) #10000
    routes = controller.requirement2(control, station_name, min_stations, max_time) 
    print(f'In total are {lt.size(routes)} routes available: \n')
    for route in lt.iterator(routes):
        print(f'Total time -> {route[0]} | Total stations: {lt.size(route[1])}')
        for station in lt.iterator(route[1]):
            """
            id = station.split['-'][0]
            name = station.split['-'][1]
            print(f'id -> {id} | name -> {name}')
            """
            print(station)
        print('\n--------------------------------------------------------------------------------------------------\n')

def optionThree(control):
    #print('El número de componentes conectados es: ' + str(controller.requirement3(control)))
    #print(control['components'])
    tabla_hash_componentes = controller.requirement3(control) 
    numero_componentes_conectados = lt.size(mp.keySet(tabla_hash_componentes))
    print("El número total de componentes fuertemente conectados es: ", numero_componentes_conectados)
    for componente in lt.iterator(mp.keySet(tabla_hash_componentes)):
        numero_estaciones = me.getValue(mp.get(tabla_hash_componentes,componente))[0]
        viajes_inician = me.getValue(mp.get(tabla_hash_componentes,componente))[1]
        viajes_inician = viajes_inician.split('-')
        viajes_terminan = me.getValue(mp.get(tabla_hash_componentes,componente))[2]
        viajes_terminan = viajes_terminan.split('-')
        print("El número de estaciones del componente ", componente , " es : ", numero_estaciones)
        print("El ID y el nombre de la estación donde más viajes inician es: ")
        print("ID: ", viajes_inician[0])
        print("Nombre: ", viajes_inician[1])
        print("El ID y el nombre de la estación donde más viajes terminan es: ")
        print("ID: ", viajes_terminan[0])
        print("Nombre: ", viajes_terminan[1])
        print('--------------------------------------------------------------------------------------------------')

def optionFour(control):
    origin_station = input('Enter origin station: ') #York St / Lake Shore Blvd W
    arrival_station = input('Enter arrival station: ') #Davenport Rd / Avenue Rd
    path = controller.requirement4(control, origin_station, arrival_station)
    print(f'\nThe average time for the trip is {int(path[1])} minutes')
    for station in lt.iterator(path[0]):
        if station[0] != 0:
            print(f'Station -> {station[1]} / Time for next station -> {int(station[0])} minutes')
        else:
            print(f'Last Station -> {station[1]}')

def optionFive(control):
    initial_date = input('Enter the initial date: ') #01/01/2021
    final_date = input('Enter the final date: ') #01/02/2021
    dates = controller.requirement5(control, initial_date, final_date)
    print(f'\nTotal trips between {initial_date} - {final_date}: {dates[4]}')
    print(f'Total duration between {initial_date} - {final_date}: {dates[5]}')
    print('\n----------------------------------------------------------------------------------\n')
    num_origin = me.getKey(dates[0])
    list_origin = me.getValue(dates[0])
    print(f'\nThe stations with more started trips with the are: ')
    print(f'Number trips: {num_origin}')
    for station in lt.iterator(list_origin):
        print(f'Origin station -> {station} / Number trips -> {num_origin}')
    print('\n----------------------------------------------------------------------------------\n')
    num_arrival = me.getKey(dates[1])
    list_arrival = me.getValue(dates[1])
    print(f'\nThe stations with more finished trips are: ')
    print(f'Number trips: {num_arrival}')
    for station in lt.iterator(list_arrival):
        print(f'Arrival station -> {station} / Number trips -> {num_arrival}')
    print('\n----------------------------------------------------------------------------------\n')
    num_initial_hour = me.getKey(dates[2])
    list_initial_hour = me.getValue(dates[2])
    print(f'\nThe hours with more started trips are: ')
    print(f'Number trips: {num_initial_hour}')
    for hour in lt.iterator(list_initial_hour):
        print(f'Hour -> {hour} / Number trips -> {num_initial_hour}')
    print('\n----------------------------------------------------------------------------------\n')
    num_final_hour = me.getKey(dates[3])
    list_final_hour = me.getValue(dates[3])
    print(f'\nThe hours with more finished trips are: ')
    print(f'Number trips: {num_final_hour}')
    for hour in lt.iterator(list_final_hour):
        print(f'Hour -> {hour} / Number trips -> {num_final_hour}')
    print('\n----------------------------------------------------------------------------------\n')

def optionSix(control):
    bike_id = input('Enter the bike id: ') #25
    bike_id_format = bike_id+'.0'
    bike = controller.requirement6(control, bike_id_format)
    print(f'\nTotal trips with the bike {bike_id}: {int(bike[0])}')
    print(f'Total time with the bike {bike_id}: {int(bike[1]) // 60} hours and {int(bike[1]) % 60} minutes')
    print('\n----------------------------------------------------------------------------------\n')
    num_origin = me.getKey(bike[2])
    list_origin = me.getValue(bike[2])
    print(f'\nThe stations with more started trips with the bike are: ')
    print(f'Number trips: {num_origin}')
    for station in lt.iterator(list_origin):
        print(f'Origin station -> {station} / Number trips -> {num_origin}')
    print('\n----------------------------------------------------------------------------------\n')
    num_arrival = me.getKey(bike[3])
    list_arrival = me.getValue(bike[3])
    print(f'\nThe stations with more finished trips with the bike are: ')
    print(f'Number trips: {num_arrival}')
    for station in lt.iterator(list_arrival):
        print(f'Arrival station -> {station} / Number trips -> {num_arrival}')
    print('\n----------------------------------------------------------------------------------\n')

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------

def loadData():
    trips = controller.loadData(control)
    return trips

"""
Menu principal
"""
while True:
    printMenu()
    inputs = input('Select an option to continue: \n')
    if int(inputs[0]) == 0:
        control = newController()

        start_time = getTime()

        print("\nLoading Data....\n")
        trips = loadData()
        charge = controller.requirement0(control)

        stop_time = getTime()

        print(f'There are {charge[0]} vertices')
        print(f'There are {charge[1]} edges')
        print(f'There are {trips[0]} trips with duration 0.0')
        print(f'There are {trips[2]} trips with incomplete information')
        print(f'There are {trips[3]} trips with self-referenced data')
        print(f'Only where charged {trips[1]} trips')
        print(f'In total are {trips[0] + trips[1]} trips\n')

        vertices_list = control['vertices_list']
        first_five = lt.subList(vertices_list, 1, 5)
        for station in lt.iterator(first_five):
            print(station)
        print('\n-----------------------------------------------------------------------\n')
        last_five = lt.subList(vertices_list, -4, 5)
        for station in lt.iterator(last_five):
            print(station)
        
        delta_time = deltaTime(stop_time, start_time)
        print(delta_time)
       
    elif int(inputs[0]) == 1:
        optionOne(control)
        
    elif int(inputs[0]) == 2:
        optionTwo(control)
    
    elif int(inputs[0]) == 3:
        optionThree(control)

    elif int(inputs[0]) == 4:
        optionFour(control)

    elif int(inputs[0]) == 5:
        optionFive(control)
        
    elif int(inputs[0]) == 6:
        optionSix(control)
    
    elif int(inputs[0]) == 7:
        pass
        
    else:
        sys.exit(0)
sys.exit(0)