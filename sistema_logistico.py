import sys

# Clase Pila
class Pila:
    def __init__(self):
        self.datos = []

    def push(self, dato):
        self.datos.append(dato)

    def pop(self):
        if self.__is_empty():
            return None
        return self.datos.pop(-1)

    def __is_empty(self) ->bool:
        return len(self.datos) == 0

# Clase Cola
class Cola:
    def __init__(self):
        self.datos = []


def mostrar_menu():
    print("\n========================================")
    print("   SISTEMA DE GESTIÓN LOGÍSTICA - CONSOLA")
    print("========================================")
    print("1. Apilar caja (Agregar a la cima del almacén)")
    print("2. Retirar caja de la cima")
    print("3. LLegada de camión (Añadir a la fila)")
    print("4. Despachar primer camión")
    print("5. Ver estado actual (Almacén y Camiones)")
    print("6. Salir del programa")
    print("========================================")

def ejecutar_sistema():
    # Estructuras de datos principales
    # Almacén: LIFO (último en entrar, primero en salir) -> Usamos una lista de Python
    almacen_cajas = []
    
    # Cola de camiones: FIFO (primero en llegar, primero en ser atendido) -> Usamos una lista como cola
    fila_camiones = []

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        # Validación de entrada para evitar que el programa colapse
        if not opcion.isdigit():
            print("\n[ERROR] Opción inválida. Por favor, ingrese un número del 1 al 6.")
            continue

        opcion = int(opcion)

        if opcion == 1:
            # Apilar caja (LIFO)
            nombre_caja = input("Ingrese el nombre/identificador de la caja (ej. CAJA-101): ").strip()
            if not nombre_caja:
                print("\n[ERROR] El nombre de la caja no puede estar vacío.")
                continue
            almacen_cajas.append(nombre_caja)
            print(f"\n[ÉXITO] La caja '{nombre_caja}' fue apilada con éxito en la cima.")

        elif opcion == 2:
            # Retirar caja de la cima (LIFO)
            if len(almacen_cajas) == 0:
                print("\n[AVISO] El almacén está vacío. No hay cajas para retirar.")
            else:
                caja_retirada = almacen_cajas.pop()
                print(f"\n[ÉXITO] Caja retirada de la cima: '{caja_retirada}'.")

        elif opcion == 3:
            # Llegada de camión (FIFO)
            placa_camion = input("Ingrese la placa o identificador del camión (ej. CAMION-ALPHA): ").strip()
            if not placa_camion:
                print("\n[ERROR] La placa del camión no puede estar vacía.")
                continue
            fila_camiones.append(placa_camion)
            print(f"\n[ÉXITO] Camión '{placa_camion}' formado en la fila de espera.")

        elif opcion == 4:
            # Despachar primer camión (FIFO)
            if len(fila_camiones) == 0:
                print("\n[AVISO] No hay camiones esperando en la fila.")
            else:
                camion_despachado = fila_camiones.pop(0)
                print(f"\n[ÉXITO] Camión despachado: '{camion_despachado}'.")

        elif opcion == 5:
            # Ver estado actual
            print("\n--- ESTADO ACTUAL DEL CENTRO DE DISTRIBUCIÓN ---")
            print(f"Cajas apiladas (Cima al final): {almacen_cajas}")
            print(f"Camiones en fila (Frente al inicio): {fila_camiones}")
            print("-------------------------------------------------")

        elif opcion == 6:
            # Salir
            print("\nGracias por utilizar el Sistema de Gestión Logística. ¡Hasta luego!")
            sys.exit()

        else:
            print("\n[ERROR] Opción fuera de rango. Seleccione un número entre 1 y 6.")

if __name__ == "__main__":
    ejecutar_sistema()