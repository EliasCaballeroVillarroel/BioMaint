from models.equipos import Equipo
"""
def mostrar_menu():
    print("== BioMaint ==")
    print(
    "1. Crear equipo"
    "\n2. Mostrar equipo"
    "\n3. Buscar equipo"
    "\n4. Salir"
    )
    print("Escribi el numero de opción a elegir ")

def crear_equipo():
    print("Ingrese el equipo")
    equipo = Equipo(
                pedir_texto("Ingrese el nombre del equipo: "),
                pedir_id(),
                pedir_texto("Ingrese el número de serie del equipo: "),
                pedir_texto("Ingrese la clínica/hospital del equipo: "),
                pedir_texto("Ingrese el modelo del equipo: "))
    
    while True:
        if id_existe(equipo.equipo_id):
            print("El ID ya está cargado ingrese uno nuevo")
            equipo.equipo_id = pedir_id()
            continue
        if ns_existe(equipo.serie):
            print("El NS ya está cargado ingrese uno nuevo")
            equipo.serie = pedir_texto("Ingrese el número de serie del equipo: ")
            continue
        return equipo 


def buscar_equipo():
    id_busc = pedir_id()

    for equipo in equipos:
        if id_busc == equipo.equipo_id:
            print(equipo.mostrar_info())
            return
    print("No se encontró un equipo con ese ID.")

def pedir_texto(mensaje):
    while True:
        dato = input(mensaje).strip()

        if dato == "":
            print("No puede estar vacío. Ingrese nuevamente.")
            continue

        return dato

def pedir_id():
    while True:
        id_ingresado = input("Ingrese el ID: ").strip()

        if id_ingresado == "":
            print("El ID no puede estar vacío.")
            continue

        if not id_ingresado.isdigit():
            print("El ID debe contener solo números.")
            continue

        return id_ingresado.zfill(4)
    
def id_existe(id_buscado):
    for equipo in equipos:
        if equipo.equipo_id == id_buscado:
            return True
    return False

def ns_existe(NS_buscado):
    for equipo in equipos:
        if equipo.serie == NS_buscado:
            return True
    return False
    
    
opcion = None
id_ingresado = None
equipos = []
while opcion != 3:
    mostrar_menu()
    opcion=int(input())
    if opcion == 1:
        equipo=crear_equipo()
        equipos.append(equipo) 
    elif opcion == 2:
        if equipos: 
            for i in equipos:
                print(i.mostrar_info())
        else: 
            print("No hay un equipo registrado")
    elif opcion == 3:
        buscar_equipo()
    elif opcion == 4: 
        print("Volviendo al menu principal")
        break
    else: 
        print("Ingrese una opción valida")
"""
from database.db import get_connection 
conection = get_connection()

print("Conexión exitosa a la base de datos")
conection.close()

