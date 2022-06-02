from mimetypes import init
import config as cf
import sys
import controller
import time
assert cf
from DISClib.ADT import list as lt
from DISClib.DataStructures import mapentry as me

# -----------------------------------------------------
# NEW CONTROLLER
# -----------------------------------------------------

def newController():
    control = controller.newController()
    return control

# -----------------------------------------------------
# TIME FUNCTIONS
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
# LOAD DATA
# -----------------------------------------------------

def loadData():
    trips = controller.loadData(analyzer)
    return trips

def optionOne(analyzer):
    stations = controller.requirement1(analyzer)
    for station in lt.iterator(stations):
        station_id = station[0].split('-')[0]
        station_name = station[0].split('-')[1]
        outdegree = station[6]
        suscribers_count = station[4]
        tourist_count = station[3]
        total_count = station[5]
        hours = station[1]
        dates = station[2]
        print(f'id -> {station_id} | name -> {station_name} | out trips -> {total_count} | suscribers trips -> {suscribers_count} | tourist trips -> {tourist_count} |  outdegree -> {outdegree} | rush hour -> {hours[0], hours[1][0]} | rush date -> {dates[0], dates[1][0]}')

def optionTwo(analyzer):
    origin_station = input('Enter origin station: ')
    max_time = int(input('Enter max time: '))
    min_stations = int(input('Enter min stations: '))
    max_routes = int(input('Enter max routes: '))
    routes = controller.requirement2(analyzer, origin_station, max_time, min_stations, max_routes)
    total_routes = routes[0]
    user_routes = routes[1]

    print(f'\nThere are in total {total_routes} routes\n')

    for path in lt.iterator(user_routes):
        path_duration = path[0]
        print(f'\n The trip duration is: {path_duration}')
        print(f'\n The round trip duration is: {path_duration * 2}')
        path_stations = path[1]
        path_len = lt.size(path[1]) + 1
        print(f'\n The trip len is: {path_len}\n')
        for station in lt.iterator(path_stations):
            init_station = station[1]
            finish_station = station[2]
            weigth = station[0]
            print(f'Init Station: {init_station} | Time for next station: {weigth} | Next Station: {finish_station}')

        print('---------------------------------------------------------------------------------------------------------')

def optionThree(control):
    def printReq3(lista_componentes_conectados):
        for componente in lt.iterator(lista_componentes_conectados):
            numero_estaciones = componente[0]
            viajes_inician = componente[1]
            viajes_inician = viajes_inician.split('-')
            viajes_terminan = componente[2]
            viajes_terminan = viajes_terminan.split('-')
            print("El número de estaciones del componente es :", numero_estaciones)
            print("El ID y el nombre de la estación donde más viajes inician es: ")
            print("ID: ", viajes_inician[0])
            print("Nombre: ", viajes_inician[1])
            print("El ID y el nombre de la estación donde más viajes terminan es: ")
            print("ID: ", viajes_terminan[0])
            print("Nombre: ", viajes_terminan[1])
            print('--------------------------------------------------------------------------------------------------')
            
    lista_componentes_conectados = controller.requirement3(control) 
    numero_componentes_conectados = lt.size(lista_componentes_conectados)
    print("There are", numero_componentes_conectados, "Strongly Connected Componentes (SCC) in the graph.")
    print('--------------------------------------------------------------------------------------------------')

    if numero_componentes_conectados < 6:
        printReq3(lista_componentes_conectados)
    else: 
        lista_primeros3 = lt.newList('ARRAY_LIST')
        lista_ultimos3 = lt.newList('ARRAY_LIST')
        for pos in range(1, numero_componentes_conectados):
            if pos > 3:
                pass
            else:
                firstcomponent = lt.getElement(lista_componentes_conectados, pos)
                lt.addLast(lista_primeros3, firstcomponent)
            if pos < numero_componentes_conectados - 3:
                pass
            else:
                lastcomponent = lt.getElement(lista_componentes_conectados, pos)
                lt.addLast(lista_ultimos3, lastcomponent)
        print("The first 3 and last 3 of the SCC are:")
        printReq3(lista_primeros3)
        printReq3(lista_ultimos3)
        

def optionFour(analyzer):
    origin_station = input('Enter origin station: ') #York St / Lake Shore Blvd W
    arrival_station = input('Enter arrival station: ') #Davenport Rd / Avenue Rd
    path = controller.requirement4(analyzer, origin_station, arrival_station)
    print(f'\nThe average time for the trip is {int(path[1])} minutes')
    for station in lt.iterator(path[0]):
        if station[0] != 0:
            print(f'Station -> {station[1]} / Time for next station -> {int(station[0])} minutes')
        else:
            print(f'Last Station -> {station[1]}')

def optionFive(analyzer):
    init_date = input('Enter the initial date: ')
    finish_date = input('Enter the finish date: ')
    interval = controller.requirement5(analyzer, init_date, finish_date)
    out_hours = interval[0]
    out_stations = interval[1]
    in_hours = interval[2]
    in_stations = interval[3]
    total_time = interval[4]
    total_trips = interval[5]

    print(f'\nIn total are {total_trips} trips between {init_date} - {finish_date}')
    print(f'In total all the trips duration is {total_time}\n')

    print('\nOUT TRIPS INFO:')
    print('-------------------------------------------------------------------------------------')

    print(f'\nThe station(s) with more out trips is:')
    for station in lt.iterator(out_stations[1]):
        print(f'{station} with {out_stations[0]} trips')

    print(f'\nThe hour with more out trips is: ')
    for hour in lt.iterator(out_hours[1]):
        print(f'{hour} with {out_hours[0]} trips')

    print('\nIN TRIPS INFO:')
    print('-------------------------------------------------------------------------------------')

    print(f'\nThe station(s) with more in trips is:')
    for station in lt.iterator(in_stations[1]):
        print(f'{station} with {in_stations[0]} trips')

    print(f'\nThe hour with more in trips is: ')
    for hour in lt.iterator(in_hours[1]):
        print(f'{hour} with {in_hours[0]} trips')
    print('\n-------------------------------------------------------------------------------------\n')

def optionSix(analyzer):
    bike_id = int(float(input('Enter the bike id: '))) #25
    bike = controller.requirement6(analyzer, bike_id)
    print(f'\nTotal trips with the bike {bike_id}: {int(bike[0])}')
    print(f'Total time with the bike {bike_id}: {bike[1]}')
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

def optionSeven(analyzer):
    init_date = input('Enter the initial date: ')
    finish_date = input('Enter the finish date: ')
    station = input('Enter station: ')
    interval = controller.requirement7(analyzer, init_date, finish_date, station)

# -----------------------------------------------------
# MENU
# -----------------------------------------------------
while True:
    printMenu()
    inputs = input('Select an option to continue: \n')
    if int(inputs[0]) == 0:
        analyzer = newController()

        start_time = getTime()

        print("\nLoading Data....\n")
        trips = loadData()
        charge = controller.charge(analyzer)

        stop_time = getTime()

        print(f'Trips Filter:')
        print(f'There are {trips[0]} trips with duration 0.0')
        print(f'There are {trips[2]} trips with incomplete information')
        print(f'There are {trips[3]} trips with self-referenced data')
        print(f'Only where charged {trips[1]} trips')
        print(f'In total are {trips[4] + trips[1]} trips')
        print('-----------------------------------------------------------------------------\n')
        print(f'Digraph Info:')
        print(f'There are {charge[0]} vertices')
        print(f'There are {charge[1]} edges')
        print('-----------------------------------------------------------------------------\n')
    

        for station in lt.iterator(charge[4]):
          station_id = station['station_id']
          station_name = station['station_name']
          station_indegree = station['indegree']
          station_outdegree = station['outdegree']
          station_out = station['out_trips']
          station_in = station['in_trips']
          print(f'Station Id: {station_id} | Station Name: {station_name} | Indegree: {station_indegree} | Outdegree: {station_outdegree} | In Trips: {station_in} | Out Trips: {station_out}')

        print('----------------------------------------------------------------------------\n')
        
    elif int(inputs[0]) == 1:
        optionOne(analyzer)
        
    elif int(inputs[0]) == 2:
        optionTwo(analyzer)
    
    elif int(inputs[0]) == 3:
        optionThree(analyzer)

    elif int(inputs[0]) == 4:
        optionFour(analyzer)

    elif int(inputs[0]) == 5:
        optionFive(analyzer)
        
    elif int(inputs[0]) == 6:
        optionSix(analyzer)
    
    elif int(inputs[0]) == 7:
        optionSeven(analyzer)
        
    else:
        sys.exit(0)
sys.exit(0)