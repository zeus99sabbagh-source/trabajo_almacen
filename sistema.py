# SISTEMA DE DESPACHO Y ALMACÉN
# Simulador de consola de Pila (LIFO) y Cola (FIFO)

import re

MAX_LARGO = 25
PATRON_NOMBRE = re.compile(r"[\w .\-#/]+")   # letras, números, espacios y - _ . # /


# ---------- PILA (LIFO) ----------
class Pila:
    def __init__(self):
        self.datos = []

    def push(self, dato):
        self.datos.append(dato)

    def pop(self):
        if self.esta_vacia():
            return None
        return self.datos.pop()

    def esta_vacia(self):
        return len(self.datos) == 0

    def mostrar(self):
        # De la cima a la base
        return list(reversed(self.datos))


# ---------- COLA (FIFO) ----------
class Cola:
    def __init__(self):
        self.datos = []

    def enqueue(self, dato):
        self.datos.append(dato)

    def dequeue(self):
        if self.esta_vacia():
            return None
        return self.datos.pop(0)

    def esta_vacia(self):
        return len(self.datos) == 0

    def mostrar(self):
        # Del frente al fin
        return list(self.datos)


# ---------- VALIDACIONES ----------
def pedir_nombre(mensaje, existentes):
    """Pide un nombre y lo valida. Devuelve el nombre limpio o None si se cancela."""
    for intento in range(3):
        nombre = " ".join(input(mensaje).split())   # quita espacios de más

        if nombre == "":
            print("[!] Error: El nombre no puede estar vacío.")
        elif len(nombre) > MAX_LARGO:
            print(f"[!] Error: El nombre es muy largo (máximo {MAX_LARGO} caracteres).")
        elif not PATRON_NOMBRE.fullmatch(nombre):
            print("[!] Error: Solo se permiten letras, números, espacios y los símbolos - _ . # /")
        elif not any(c.isalnum() for c in nombre):
            print("[!] Error: El nombre debe tener al menos una letra o un número.")
        else:
            if nombre.lower() in [e.lower() for e in existentes]:
                print(f"[!] Aviso: [{nombre}] ya existe.")
                respuesta = input("¿Agregarlo de todos modos? (s/n): ").strip().lower()
                if respuesta not in ("s", "si", "sí"):
                    print("Operación cancelada.")
                    return None
            return nombre

        if intento < 2:
            print(f"Intente de nuevo ({intento + 2}/3).")

    print("Demasiados intentos inválidos. Volviendo al menú.")
    return None


# ---------- MENÚ ----------
def mostrar_menu():
    print()
    print("=" * 50)
    print("        SISTEMA DE DESPACHO Y ALMACÉN")
    print("=" * 50)
    print("1. [PILA] Apilar caja (push)")
    print("2. [PILA] Retirar caja de la cima (pop)")
    print("3. [COLA] Llega camión a la fila (enqueue)")
    print("4. [COLA] Despachar primer camión (dequeue)")
    print("5. Ver estado del almacén y camiones")
    print("6. Salir del programa")
    print("-" * 50)


# ---------- PROGRAMA PRINCIPAL ----------
def main():
    almacen = Pila()
    fila = Cola()

    try:
        while True:
            mostrar_menu()
            opcion = input("Seleccione una opción (1-6): ").strip()

            if opcion == "1":
                caja = pedir_nombre("Identificador de la caja (ej. Caja-101): ", almacen.mostrar())
                if caja is not None:
                    almacen.push(caja)
                    print(f"-> Caja [{caja}] apilada con éxito.")

            elif opcion == "2":
                caja = almacen.pop()
                if caja is None:
                    print("[!] Error: El almacén está vacío (no hay cajas que retirar).")
                else:
                    print(f"-> Caja [{caja}] retirada de la cima.")

            elif opcion == "3":
                camion = pedir_nombre("Placa o identificador del camión (ej. Camión-Alfa): ", fila.mostrar())
                if camion is not None:
                    fila.enqueue(camion)
                    print(f"-> Camión [{camion}] formado en la fila.")

            elif opcion == "4":
                camion = fila.dequeue()
                if camion is None:
                    print("[!] Error: No hay camiones esperando turno.")
                else:
                    print(f"-> Camión [{camion}] despachado.")

            elif opcion == "5":
                print("-" * 50)
                print("ESTADO ACTUAL:")
                print(f"- Cajas apiladas (Cima -> Base): {almacen.mostrar()}")
                print(f"- Fila de camiones (Frente -> Fin): {fila.mostrar()}")
                print("-" * 50)

            elif opcion == "6":
                break

            elif opcion == "":
                print("[!] Error: No escribió nada. Ingrese un número del 1 al 6.")
            elif not opcion.isdigit():
                print(f"[!] Error: '{opcion}' no es una opción válida. Ingrese un número del 1 al 6.")
            else:
                print("[!] Error: Opción fuera de rango. Elija entre 1 y 6.")

    except (KeyboardInterrupt, EOFError):
        print()   # Ctrl+C o Ctrl+D: se sale sin mostrar errores

    print("Gracias por usar el sistema. ¡Hasta pronto!")


if __name__ == "__main__":
    main()
