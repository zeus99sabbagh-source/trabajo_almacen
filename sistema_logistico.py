import sys

# Clase Pila
class Stack:
    def __init__(self):
        self.datos = []

    def push(self, dato):
        self.datos.append(dato)

    def pop(self):
        if self.__is_empty():
            return None
        return self.datos.pop(-1)

    def top(self):
        if self.__is_empty():
            return None
        return self.datos[-1]

    def __is_empty(self) -> bool:
        return len(self.datos) == 0

# Clase Cola
class Queue:
    def __init__(self):
        self.datos = []

    def enqueue(self, dato):
        self.datos.append(dato)

    def dequeue(self):
        if self.__is_empty():
            return None
        return self.datos.pop(0)

    def first(self):
        if self.__is_empty():
            return None
        return self.datos[0]

    def __is_empty(self) -> bool:
        return len(self.datos) == 0


def mostrar_menu():
    print("\n========================================")
    print("  SISTEMA DE GESTIÓN LOGÍSTICA - CONSOLA")
    print("========================================")
    print("1. Apilar caja (Agregar a la cima del almacén)")
    print("2. Retirar caja de la cima")
    print("3. Llegada de camión (Añadir a la fila)")
    print("4. Despachar primer camión")
    print("5. Consultas, Estadísticas e Historial")
    print("6. Salir del programa")
    print("========================================")

def ejecutar_sistema():
    # Estructuras de datos principales
    almacen_cajas = []
    fila_camiones = []
    historial_movimientos = []
    
    # Diccionario para llevar el conteo de cada opción seleccionada
    contador_opciones = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción (1-6): ").strip()

        # Validación de entrada para evitar que el programa colapse
        if not opcion.isdigit():
            print("\n[ERROR] Opción inválida. Por favor, ingrese un número del 1 al 6.")
            continue

        opcion = int(opcion)

        # Validar que esté en el rango correcto antes de contar
        if opcion < 1 or opcion > 6:
            print("\n[ERROR] Opción fuera de rango. Seleccione un número entre 1 y 6.")
            continue

        # Incrementamos el contador de la opción seleccionada
        contador_opciones[opcion] += 1

        if opcion == 1:
            # Apilar caja (LIFO)
            nombre_caja = input("Ingrese el nombre/identificador de la caja (ej. CAJA-101): ").strip()
            if not nombre_caja:
                print("\n[ERROR] El nombre de la caja no puede estar vacío.")
                contador_opciones[1] -= 1
                continue
            almacen_cajas.append(nombre_caja)
            historial_movimientos.append(f"Caja APILADA: {nombre_caja}")
            print(f"\n[ÉXITO] La caja '{nombre_caja}' fue apilada con éxito en la cima.")

        elif opcion == 2:
            # Retirar caja de la cima (LIFO)
            if len(almacen_cajas) == 0:
                print("\n[AVISO] El almacén está vacío. No hay cajas para retirar.")
            else:
                caja_retirada = almacen_cajas.pop()
                historial_movimientos.append(f"Caja RETIRADA: {caja_retirada}")
                print(f"\n[ÉXITO] Caja retirada de la cima: '{caja_retirada}'.")

        elif opcion == 3:
            # Llegada de camión (FIFO)
            placa_camion = input("Ingrese la placa o identificador del camión (ej. CAMION-ALPHA): ").strip()
            if not placa_camion:
                print("\n[ERROR] La placa del camión no puede estar vacía.")
                contador_opciones[3] -= 1
                continue
            fila_camiones.append(placa_camion)
            historial_movimientos.append(f"Camión LLEGADA: {placa_camion}")
            print(f"\n[ÉXITO] Camión '{placa_camion}' formado en la fila de espera.")

        elif opcion == 4:
            # Despachar primer camión (FIFO)
            if len(fila_camiones) == 0:
                print("\n[AVISO] No hay camiones esperando en la fila.")
            else:
                camion_despachado = fila_camiones.pop(0)
                historial_movimientos.append(f"Camión DESPACHADO: {camion_despachado}")
                print(f"\n[ÉXITO] Camión despachado: '{camion_despachado}'.")

        elif opcion == 5:
            # Submenú para Estado, Estadísticas e Historial
            while True:
                print("\n========================================")
                print("     SUBMENÚ: REPORTES Y CONSULTAS")
                print("========================================")
                print("1. Ver estado actual (Almacén y Camiones)")
                print("2. Ver estadísticas de uso (Contadores)")
                print("3. Ver historial de movimientos")
                print("4. Volver al menú principal")
                print("========================================")
                
                sub_opcion = input("Elija una opción del submenú (1-4): ").strip()

                if sub_opcion == "1":
                    print("\n--- ESTADO ACTUAL DEL CENTRO DE DISTRIBUCIÓN ---")
                    print(f"Cajas apiladas (Cima al final): {almacen_cajas}")
                    print(f"Camiones en fila (Frente al inicio): {fila_camiones}")
                    print("-------------------------------------------------")

                elif sub_opcion == "2":
                    print("\n--- ESTADÍSTICAS DE USO (VECES SELECCIONADAS) ---")
                    print(f"• Apilar cajas (Opción 1): {contador_opciones[1]} veces")
                    print(f"• Retirar cajas (Opción 2): {contador_opciones[2]} veces")
                    print(f"• Llegadas de camión (Opción 3): {contador_opciones[3]} veces")
                    print(f"• Despachos de camión (Opción 4): {contador_opciones[4]} veces")
                    print(f"• Consultar reportes (Opción 5): {contador_opciones[5]} veces")
                    print("-------------------------------------------------")

                elif sub_opcion == "3":
                    print("\n--- HISTORIAL DE MOVIMIENTOS ---")
                    if len(historial_movimientos) == 0:
                        print("Aún no se han registrado movimientos en el sistema.")
                    else:
                        print("1. Ver orden cronológico (Antiguos primero)")
                        print("2. Ver orden inverso (Más recientes primero)")
                        print("3. Filtrar solo movimientos de Cajas")
                        print("4. Filtrar solo movimientos de Camiones")
                        filtro_historial = input("Elija una forma de visualización (1-4) o presione Enter para ver todo: ").strip()

                        print("\n--- REGISTRO DE EVENTOS ---")
                        if filtro_historial == "2":
                            movimientos_a_mostrar = reversed(historial_movimientos)
                        elif filtro_historial == "3":
                            movimientos_a_mostrar = [m for m in historial_movimientos if "Caja" in m]
                        elif filtro_historial == "4":
                            movimientos_a_mostrar = [m for m in historial_movimientos if "Camión" in m]
                        else:
                            movimientos_a_mostrar = historial_movimientos

                        encontrados = False
                        for idx, movimiento in enumerate(movimientos_a_mostrar, 1):
                            print(f"[{idx}] {movimiento}")
                            encontrados = True
                        
                        if not encontrados:
                            print("No hay registros que coincidan con el filtro seleccionado.")
                    print("-------------------------------------------------")

                elif sub_opcion == "4":
                    print("\nRegresando al menú principal...")
                    break
                else:
                    print("\n[ERROR] Opción inválida en el submenú. Ingrese un número entre 1 y 4.")

        elif opcion == 6:
            # Salir
            print("\nGracias por utilizar el Sistema de Gestión Logística. ¡Hasta luego!")
            print(f"(Estadísticas finales de uso: {contador_opciones})")
            sys.exit()

if __name__ == "__main__":
    ejecutar_sistema()
