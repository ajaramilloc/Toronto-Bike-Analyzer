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
from DISClib.ADT import graph as gr
assert cf

# -----------------------------------------------------
# NEW CONTROLLER
# -----------------------------------------------------

def newController():
    control = controller.newController()
    return control

def printMenu():
    print("Bienvenido")
    print("1- Cargar información en el catálogo")
    print("2- Comprar bicicletas para las estaciones con más viajes de origen")
    print("3- Planear paseos turísticos por la ciudad")
    print("4- Reconocer los componentes fuertemente conectados")
    print("5- Planear una ruta rápida para el usuario")
    print("6- Reportar rutas en un rango de fechas para los usuarios anuales")
    print("7- Planear el mantenimiento preventivo de bicicleta")
    print("8- La estación más frecuentada por los visitantes")

# -----------------------------------------------------
# GENERIC FUNCTIONS
# -----------------------------------------------------

# -----------------------------------------------------
# PRINT FUNCTIONS
# -----------------------------------------------------

def optionThree(control):
    print('El número de componentes conectados es: ' + str(controller.requirement3(control)))

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
        print("\nLoading Data....\n")
        trips = loadData()
        charge = controller.requirement0(control)
        print(f'There are {charge[0]} vertices')
        print(f'There are {charge[1]} edges')
        print(f'There are {trips[0]} trips with no duration or self-referenced vertex')
        print(f'Only where charged {trips[1]} trips')
        print(f'In total are {trips[0] + trips[1]} trips\n')
        
    elif int(inputs[0]) == 1:
        pass
        
    elif int(inputs[0]) == 2:
        pass
    
    elif int(inputs[0]) == 3:
        optionThree(control)

    elif int(inputs[0]) == 4:
        pass

    elif int(inputs[0]) == 5:
        pass
        
    elif int(inputs[0]) == 6:
        pass
    
    elif int(inputs[0]) == 7:
        pass
        
    else:
        sys.exit(0)
sys.exit(0)