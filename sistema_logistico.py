import os
import sys
from collections import deque
from typing import Any, Optional

#Limpieza de terminal
def limpiar_pantalla() -> None:
    """Limpia la consola en Windows o Linux/macOS."""
    os.system("cls" if os.name == "nt" else "clear")

#Clase pila
class Stack:
    """Implementación de Pila (LIFO) para el Almacén de Cajas."""

    def __init__(self, capacidad_maxima: Optional[int] = None) -> None:
        self.datos = []
        self.capacidad_maxima = capacidad_maxima

    def esta_vacia(self) -> bool:
        return len(self.datos) == 0

    def esta_llena(self) -> bool:
        if self.capacidad_maxima is None:
            return False
        return len(self.datos) >= self.capacidad_maxima

    def push(self, dato: Any) -> bool:
        if self.esta_llena():
            return False
        self.datos.append(dato)
        return True

    def pop(self) -> Optional[Any]:
        if self.esta_vacia():
            return None
        return self.datos.pop()

    def top(self) -> Optional[Any]:
        if self.esta_vacia():
            return None
        return self.datos[-1]

    # Alias para compatibilidad con la especificación
    peek = top
    is_empty = esta_vacia

    def __len__(self) -> int:
        return len(self.datos)

    def __str__(self) -> str:
        # Representación de Cima a Base
        return str(self.datos[::-1])

#Clase Cola
class Queue:
    """Implementación de Cola (FIFO) con deque para la Bahía de Camiones."""

    def __init__(self, capacidad_maxima: Optional[int] = None) -> None:
        self.datos = deque()
        self.capacidad_maxima = capacidad_maxima

    def esta_vacia(self) -> bool:
        return len(self.datos) == 0

    def esta_llena(self) -> bool:
        if self.capacidad_maxima is None:
            return False
        return len(self.datos) >= self.capacidad_maxima

    def enqueue(self, dato: Any) -> bool:
        if self.esta_llena():
            return False
        self.datos.append(dato)
        return True

    def dequeue(self) -> Optional[Any]:
        if self.esta_vacia():
            return None
        return self.datos.popleft()

    def ver_frente(self) -> Optional[Any]:
        if self.esta_vacia():
            return None
        return self.datos[0]

    # Alias para compatibilidad con la especificación
    first = ver_frente
    is_empty = esta_vacia

    def __len__(self) -> int:
        return len(self.datos)

    def __str__(self) -> str:
        # Representación de Frente a Fin
        return str(list(self.datos))


#Validaciones
def pedir_opcion(minimo: int, maximo: int, mensaje: str = "Seleccione una opción: ") -> int:
    """Valida números enteros, rango y captura Ctrl+C sin colapsar."""
    while True:
        try:
            entrada = input(mensaje).strip()
            if not entrada:
                print("\n[ERROR] La opción no puede estar vacía.")
                continue

            opcion = int(entrada)
            if minimo <= opcion <= maximo:
                return opcion
            print(f"\n[ERROR] Opción fuera de rango. Seleccione un número entre {minimo} y {maximo}.")
        except ValueError:
            print(f"\n[ERROR] Opción inválida. Por favor, ingrese un número del {minimo} al {maximo}.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[AVISO] Interrupción detectada (Ctrl+C). Regresando...")
            return maximo


def pedir_identificador(
    tipo: str,
    estructura: Any,
    longitud_min: int = 2,
    longitud_max: int = 30,
) -> Optional[str]:
    """Valida vacíos, longitud, duplicados y captura Ctrl+C."""
    while True:
        try:
            ejemplo = "ej. CAJA-101" if "caja" in tipo.lower() else "ej. CAMION-ALPHA"
            valor = input(f"Ingrese el nombre/identificador de {tipo} ({ejemplo}): ").strip()

            if not valor:
                print(f"\n[ERROR] El identificador de {tipo} no puede estar vacío.")
                continue

            if len(valor) < longitud_min or len(valor) > longitud_max:
                print(f"\n[ERROR] La longitud debe tener entre {longitud_min} y {longitud_max} caracteres.")
                continue

            # Revisión de duplicados
            elementos = getattr(estructura, "datos", estructura)
            if valor in elementos:
                print(f"\n[ERROR] El identificador '{valor}' ya existe en el sistema.")
                continue

            return valor

        except (KeyboardInterrupt, EOFError):
            print("\n[AVISO] Operación cancelada por el usuario.")
            return None


def confirmar(pregunta: str = "¿Está seguro de que desea salir?") -> bool:
    """Pide confirmación simple por consola."""
    while True:
        try:
            respuesta = input(f"{pregunta} (s/n): ").strip().lower()
            if respuesta in ("s", "si", "sí", "y", "yes"):
                return True
            if respuesta in ("n", "no"):
                return False
            print("[AVISO] Por favor responda 's' para sí o 'n' para no.")
        except (KeyboardInterrupt, EOFError):
            print("\n[AVISO] Operación cancelada.")
            return False


#Menú
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
    # Estructuras de datos instanciadas con las clases
    almacen_cajas = Stack()
    fila_camiones = Queue()
    historial_movimientos = []

    # Diccionario para llevar el conteo de cada opción seleccionada
    contador_opciones = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    while True:
        mostrar_menu()
        opcion = pedir_opcion(1, 6, "Seleccione una opción (1-6): ")

        # Limpia la pantalla al marcar la opción
        limpiar_pantalla()

        # Incrementamos el contador de la opción seleccionada
        contador_opciones[opcion] += 1

        if opcion == 1:
            # Apilar caja (LIFO)
            nombre_caja = pedir_identificador("la caja", almacen_cajas)
            if not nombre_caja:
                contador_opciones[1] -= 1
                continue

            almacen_cajas.push(nombre_caja)
            historial_movimientos.append(f"Caja APILADA: {nombre_caja}")
            print(f"\n[ÉXITO] La caja '{nombre_caja}' fue apilada con éxito en la cima.")

        elif opcion == 2:
            # Retirar caja de la cima (LIFO)
            caja_retirada = almacen_cajas.pop()
            if caja_retirada is None:
                print("\n[AVISO] El almacén está vacío. No hay cajas para retirar.")[cite: 1]
            else:
                historial_movimientos.append(f"Caja RETIRADA: {caja_retirada}")
                print(f"\n[ÉXITO] Caja retirada de la cima: '{caja_retirada}'.")

        elif opcion == 3:
            # Llegada de camión (FIFO)
            placa_camion = pedir_identificador("el camión", fila_camiones)
            if not placa_camion:
                contador_opciones[3] -= 1
                continue

            fila_camiones.enqueue(placa_camion)
            historial_movimientos.append(f"Camión LLEGADA: {placa_camion}")
            print(f"\n[ÉXITO] Camión '{placa_camion}' formado en la fila de espera.")

        elif opcion == 4:
            # Despachar primer camión (FIFO)
            camion_despachado = fila_camiones.dequeue()
            if camion_despachado is None:
                print("\n[AVISO] No hay camiones esperando en la fila.")[cite: 1]
            else:
                historial_movimientos.append(f"Camión DESPACHADO: {camion_despachado}")
                print(f"\n[ÉXITO] Camión despachado: '{camion_despachado}'.")

        elif opcion == 5:
            # Submenú para Estado, Estadísticas e Historial
            while True:
                print("\n========================================")
                print("      SUBMENÚ: REPORTES Y CONSULTAS")
                print("========================================")
                print("1. Ver estado actual (Almacén y Camiones)")
                print("2. Ver estadísticas de uso (Contadores)")
                print("3. Ver historial de movimientos")
                print("4. Volver al menú principal")
                print("========================================")

                sub_opcion = pedir_opcion(1, 4, "Elija una opción del submenú (1-4): ")
                limpiar_pantalla()

                if sub_opcion == 1:
                    print("\n--- ESTADO ACTUAL DEL CENTRO DE DISTRIBUCIÓN ---")
                    print(f"Cajas apiladas (Cima -> Base): {almacen_cajas}")[cite: 1]
                    print(f"Camiones en fila (Frente -> Fin): {fila_camiones}")[cite: 1]
                    print("-------------------------------------------------")

                elif sub_opcion == 2:
                    print("\n--- ESTADÍSTICAS DE USO (VECES SELECCIONADAS) ---")
                    print(f"• Apilar cajas (Opción 1): {contador_opciones[1]} veces")
                    print(f"• Retirar cajas (Opción 2): {contador_opciones[2]} veces")
                    print(f"• Llegadas de camión (Opción 3): {contador_opciones[3]} veces")
                    print(f"• Despachos de camión (Opción 4): {contador_opciones[4]} veces")
                    print(f"• Consultar reportes (Opción 5): {contador_opciones[5]} veces")
                    print("-------------------------------------------------")

                elif sub_opcion == 3:
                    print("\n--- HISTORIAL DE MOVIMIENTOS ---")
                    if len(historial_movimientos) == 0:
                        print("Aún no se han registrado movimientos en el sistema.")
                    else:
                        print("1. Ver orden cronológico (Antiguos primero)")
                        print("2. Ver orden inverso (Más recientes primero)")
                        print("3. Filtrar solo movimientos de Cajas")
                        print("4. Filtrar solo movimientos de Camiones")
                        
                        filtro_raw = input("Elija una forma de visualización (1-4) o presione Enter para ver todo: ").strip()
                        print("\n--- REGISTRO DE EVENTOS ---")

                        if filtro_raw == "2":
                            movimientos_a_mostrar = list(reversed(historial_movimientos))
                        elif filtro_raw == "3":
                            movimientos_a_mostrar = [m for m in historial_movimientos if "Caja" in m]
                        elif filtro_raw == "4":
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

                elif sub_opcion == 4:
                    print("\nRegresando al menú principal...")
                    break

        elif opcion == 6:
            # Salir
            if confirmar("¿Está seguro de que desea salir del programa?"):
                limpiar_pantalla()
                print("\nGracias por utilizar el Sistema de Gestión Logística. ¡Hasta luego!")
                print(f"(Estadísticas finales de uso: {contador_opciones})\n")
                sys.exit(0)


if __name__ == "__main__":
    ejecutar_sistema()
