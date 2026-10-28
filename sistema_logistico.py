import os
import sys
from collections import deque
from typing import Any, Optional

#Limpia Terminal
def limpiar_pantalla() -> None:
    os.system("cls" if os.name == "nt" else "clear")

#Clase Pila
class Stack:
    def __init__(self) -> None:
        self.datos = []

    def push(self, dato: Any) -> None:
        self.datos.append(dato)

    def pop(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.datos.pop()

    def peek(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.datos[-1]

    def is_empty(self) -> bool:
        return len(self.datos) == 0

    def __len__(self) -> int:
        return len(self.datos)

    def __str__(self) -> str:
        return str(self.datos[::-1])

#Clase Cola
class Queue:
    def __init__(self) -> None:
        self.datos = deque()

    def enqueue(self, dato: Any) -> None:
        self.datos.append(dato)

    def dequeue(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.datos.popleft()

    def ver_frente(self) -> Optional[Any]:
        if self.is_empty():
            return None
        return self.datos[0]

    def is_empty(self) -> bool:
        return len(self.datos) == 0

    def __len__(self) -> int:
        return len(self.datos)

    def __str__(self) -> str:
        return str(list(self.datos))

#Validaciones
def pedir_opcion(minimo: int, maximo: int, mensaje: str = "Seleccione una opción: ") -> int:
    while True:
        try:
            entrada = input(mensaje).strip()
            if not entrada:
                print("[!] Error: No puede dejar la opción vacía.")
                continue

            opcion = int(entrada)
            if minimo <= opcion <= maximo:
                return opcion
            print(f"[!] Error: Ingrese un número entre {minimo} y {maximo}.")
        except ValueError:
            print(f"[!] Error: Entrada inválida. Ingrese un valor numérico entre {minimo} y {maximo}.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n[!] Interrupción detectada (Ctrl+C).")
            return maximo


def pedir_identificador(
    tipo: str,
    estructura_actual: Any,
    longitud_min: int = 2,
    longitud_max: int = 30,
) -> Optional[str]:
    while True:
        try:
            ejemplo = "Caja-101" if "caja" in tipo.lower() else "Camión-Alfa"
            valor = input(f"-> Ingrese identificador de {tipo} (ej. {ejemplo}): ").strip()

            if not valor:
                print(f"[!] Error: El identificador de {tipo} no puede estar vacío.")
                continue

            if len(valor) < longitud_min or len(valor) > longitud_max:
                print(f"[!] Error: La longitud debe tener entre {longitud_min} y {longitud_max} caracteres.")
                continue

            elementos = getattr(estructura_actual, "datos", estructura_actual)
            if valor in elementos:
                print(f"[!] Error: El identificador '{valor}' ya existe en el sistema.")
                continue

            return valor

        except (KeyboardInterrupt, EOFError):
            print("\n[!] Operación cancelada por el usuario.")
            return None


def confirmar(pregunta: str = "¿Desea continuar?") -> bool:
    while True:
        try:
            respuesta = input(f"{pregunta} (s/n): ").strip().lower()
            if respuesta in ("s", "si", "sí", "y", "yes"):
                return True
            if respuesta in ("n", "no"):
                return False
            print("[!] Por favor responda 's' para sí o 'n' para no.")
        except (KeyboardInterrupt, EOFError):
            print("\n[!] Operación cancelada.")
            return False

#Interfaz
def mostrar_menu() -> None:
    print("\n==================================================")
    print("        SISTEMA DE DESPACHO Y ALMACÉN")
    print("==================================================")
    print("1. [PILA] Apilar caja (push)")
    print("2. [PILA] Retirar caja de la cima (pop)")
    print("3. [COLA] Llega camión a la fila (enqueue)")
    print("4. [COLA] Despachar primer camión (dequeue)")
    print("5. Ver estado del almacén y camiones")
    print("6. Salir del programa")
    print("--------------------------------------------------")


def ejecutar_sistema() -> None:
    almacen_cajas = Stack()
    fila_camiones = Queue()
    historial_movimientos = []
    contador_opciones = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}

    while True:
        mostrar_menu()
        opcion = pedir_opcion(1, 6, "Seleccione una opción (1-6): ")
        contador_opciones[opcion] += 1

        # Limpia la pantalla inmediatamente al seleccionar la opción
        limpiar_pantalla()

        if opcion == 1:
            nombre_caja = pedir_identificador("caja", almacen_cajas)
            if nombre_caja:
                almacen_cajas.push(nombre_caja)
                historial_movimientos.append(f"Caja APILADA: {nombre_caja}")
                print(f"-> Caja [{nombre_caja}] apilada con éxito.")
            else:
                contador_opciones[1] -= 1

        elif opcion == 2:
            caja_retirada = almacen_cajas.pop()
            if caja_retirada is None:
                print("[!] Error: El almacén está vacío (no hay cajas que retirar).")
            else:
                historial_movimientos.append(f"Caja RETIRADA: {caja_retirada}")
                print(f"-> Caja [{caja_retirada}] retirada de la cima.")

        elif opcion == 3:
            placa_camion = pedir_identificador("camión", fila_camiones)
            if placa_camion:
                fila_camiones.enqueue(placa_camion)
                historial_movimientos.append(f"Camión LLEGADA: {placa_camion}")
                print(f"-> Camión [{placa_camion}] formado en la fila.")
            else:
                contador_opciones[3] -= 1

        elif opcion == 4:
            camion_despachado = fila_camiones.dequeue()
            if camion_despachado is None:
                print("[!] Error: No hay camiones esperando turno.")
            else:
                historial_movimientos.append(f"Camión DESPACHADO: {camion_despachado}")
                print(f"-> Camión [{camion_despachado}] despachado.")

        elif opcion == 5:
            print("--------------------------------------------------")
            print("ESTADO ACTUAL:")
            print(f"- Cajas apiladas (Cima -> Base): {almacen_cajas}")
            print(f"- Fila de camiones (Frente -> Fin): {fila_camiones}")
            print("--------------------------------------------------")

        elif opcion == 6:
            if confirmar("¿Está seguro de que desea salir?"):
                limpiar_pantalla()
                print("Gracias por utilizar el Sistema de Despacho y Almacén. ¡Hasta luego!\n")
                sys.exit(0)


if __name__ == "__main__":
    ejecutar_sistema()
