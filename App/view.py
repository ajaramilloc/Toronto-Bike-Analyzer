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

def optionSix(control):
    bike_id = int(float(input('Enter the bike id: '))) #25
    bike = controller.requirement6(control, bike_id)
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
        print(f'Graph Info:')
        print(f'There are {charge[2]} vertices')
        print(f'There are {charge[3]} edges')
        print('-----------------------------------------------------------------------------\n')
        

    elif int(inputs[0]) == 1:
        pass
        
    elif int(inputs[0]) == 2:
        pass
    
    elif int(inputs[0]) == 3:
        pass

    elif int(inputs[0]) == 4:
        optionFour(analyzer)

    elif int(inputs[0]) == 5:
        pass
        
    elif int(inputs[0]) == 6:
        optionSix(analyzer)
    
    elif int(inputs[0]) == 7:
        pass
        
    else:
        sys.exit(0)
sys.exit(0)