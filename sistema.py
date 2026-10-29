"""
SISTEMA DE DESPACHO Y ALMACÉN  -  Simulador de Pilas (LIFO) y Colas (FIFO)

Uso:
    python despacho_consola.py            -> consola (modo de evaluación del profesor)
    python despacho_consola.py --demo     -> arranca con datos de ejemplo
    python despacho_consola.py --test     -> pruebas automáticas del checklist

Estructura del archivo (una sección por integrante):
    PARTE 1  Clase Stack (pila)
    PARTE 2  Clase Queue (cola)
    PARTE 3  Validaciones de entrada
    PARTE 5A Bitácora (historial) y estadísticas
    PARTE 4  Interfaz de consola y bucle principal
    PARTE 5B Pruebas automáticas y arranque
"""

import builtins
import contextlib
import io
import os
import re
import sys
from collections import deque
from datetime import datetime

# ---------------------------------------------------------------------
#  CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------------
CAPACIDAD_ALMACEN = 10       # Máximo de cajas apiladas (None = sin límite)
CAPACIDAD_BAHIA = 8          # Máximo de camiones en la fila (None = sin límite)
MAX_LONGITUD_ID = 25         # Largo máximo de un identificador


# =====================================================================
#  PARTE 1: PILA (LIFO)
# =====================================================================
class Stack:
    def __init__(self, capacidad=None):
        self.__datos = []            # Privado: nadie accede a posiciones intermedias
        self.capacidad = capacidad

    def push(self, dato):
        """Apila. Devuelve False si la pila está llena."""
        if self.esta_llena():
            return False
        self.__datos.append(dato)
        return True

    def pop(self):
        """Retira la cima. Devuelve None si la pila está vacía."""
        if self.esta_vacia():
            return None
        return self.__datos.pop()

    def top(self):
        """Mira la cima sin retirarla."""
        if self.esta_vacia():
            return None
        return self.__datos[-1]

    def esta_vacia(self):
        return len(self.__datos) == 0

    def esta_llena(self):
        return self.capacidad is not None and len(self.__datos) >= self.capacidad

    def listar(self):
        """Copia para mostrar en pantalla, de la Cima a la Base."""
        return list(reversed(self.__datos))

    def __len__(self):
        return len(self.__datos)

    def __str__(self):
        return f"Stack(cima -> base): {self.listar()}"


# =====================================================================
#  PARTE 2: COLA (FIFO)
# =====================================================================
class Queue:
    def __init__(self, capacidad=None):
        self.__datos = deque()       # deque: popleft() es O(1), list.pop(0) es O(n)
        self.capacidad = capacidad

    def enqueue(self, dato):
        """Agrega al final. Devuelve False si la cola está llena."""
        if self.esta_llena():
            return False
        self.__datos.append(dato)
        return True

    def dequeue(self):
        """Atiende al primero. Devuelve None si la cola está vacía."""
        if self.esta_vacia():
            return None
        return self.__datos.popleft()

    def first(self):
        """Mira al primero sin retirarlo."""
        if self.esta_vacia():
            return None
        return self.__datos[0]

    def esta_vacia(self):
        return len(self.__datos) == 0

    def esta_llena(self):
        return self.capacidad is not None and len(self.__datos) >= self.capacidad

    def listar(self):
        """Copia para mostrar en pantalla, del Frente al Fin."""
        return list(self.__datos)

    def __len__(self):
        return len(self.__datos)

    def __str__(self):
        return f"Queue(frente -> fin): {self.listar()}"


# =====================================================================
#  PARTE 3: VALIDACIONES DE ENTRADA
# =====================================================================
_PATRON_ID = re.compile(r"[\w .\-#/]+")


def validar_identificador(texto, existentes=()):
    """
    Devuelve (identificador_limpio, mensaje_de_error, es_duplicado).
    Si hay error, el identificador es None. Los espacios son válidos
    ("Caja 1", "Camión A") y los espacios repetidos se normalizan.
    """
    limpio = " ".join(texto.split())
    if not limpio:
        return None, "[!] Error: El identificador no puede estar vacío.", False
    if len(limpio) > MAX_LONGITUD_ID:
        return None, (f"[!] Error: El identificador es muy largo "
                      f"(máximo {MAX_LONGITUD_ID} caracteres, tiene {len(limpio)})."), False
    if not _PATRON_ID.fullmatch(limpio):
        return None, "[!] Error: Solo se permiten letras, números, espacios y los símbolos - _ . # /", False
    if not any(c.isalnum() for c in limpio):
        return None, "[!] Error: El identificador debe tener al menos una letra o un número.", False
    duplicado = limpio.lower() in {e.lower() for e in existentes}
    return limpio, None, duplicado


def pedir_opcion(minimo, maximo):
    """Devuelve un entero válido o None (ya avisó del error)."""
    texto = input(f"Seleccione una opción ({minimo}-{maximo}): ").strip()
    if not texto:
        error(f"[!] Error: No escribió nada. Ingrese un número del {minimo} al {maximo}.")
        return None
    try:
        numero = int(texto)
    except ValueError:
        error(f"[!] Error: '{texto}' no es una opción válida. Ingrese un número del {minimo} al {maximo}.")
        return None
    if numero < minimo or numero > maximo:
        error(f"[!] Error: La opción {numero} está fuera de rango. Elija entre {minimo} y {maximo}.")
        return None
    return numero


def confirmar(pregunta):
    while True:
        respuesta = input(pregunta).strip().lower()
        if respuesta in ("s", "si", "sí"):
            return True
        if respuesta in ("n", "no"):
            return False
        aviso("Responda con 's' (sí) o 'n' (no).")


def pedir_identificador(pregunta, existentes=(), intentos=3):
    """Pide un identificador con reintentos. Devuelve el texto limpio o None."""
    for i in range(intentos):
        limpio, err, duplicado = validar_identificador(input(pregunta), existentes)
        if err:
            error(err)
            if i < intentos - 1:
                aviso(f"Intente de nuevo ({i + 2}/{intentos}).")
            continue
        if duplicado:
            aviso(f"[!] Aviso: [{limpio}] ya existe en esta estructura.")
            if not confirmar("¿Agregarlo de todos modos? (s/n): "):
                aviso("Operación cancelada.")
                return None
        return limpio
    aviso("Demasiados intentos inválidos. Volviendo al menú.")
    return None


# =====================================================================
#  PARTE 5A: BITÁCORA Y ESTADÍSTICAS
# =====================================================================
class Bitacora:
    def __init__(self, maximo=50):
        self._registros = deque(maxlen=maximo)

    def registrar(self, tipo, detalle):
        self._registros.append((datetime.now().strftime("%H:%M:%S"), tipo, detalle))

    def ultimas(self, cantidad=5):
        """Las últimas operaciones, de la más antigua a la más reciente."""
        return list(self._registros)[-cantidad:]


# =====================================================================
#  PARTE 4: LÓGICA CENTRAL
#  Cada operación devuelve (ok, mensaje, detalle) con los textos de la guía.
# =====================================================================
class CentroDistribucion:
    def __init__(self):
        self.almacen = Stack(CAPACIDAD_ALMACEN)
        self.fila = Queue(CAPACIDAD_BAHIA)
        self.bitacora = Bitacora()
        self.stats = {"apiladas": 0, "retiradas": 0, "llegados": 0, "despachados": 0}

    def apilar_caja(self, ident):
        if not self.almacen.push(ident):
            return False, (f"[!] Error: El almacén está lleno "
                           f"(capacidad máxima: {self.almacen.capacidad} cajas)."), ""
        self.stats["apiladas"] += 1
        self.bitacora.registrar("PUSH", ident)
        return True, f"-> Caja [{ident}] apilada con éxito.", ""

    def retirar_caja(self):
        caja = self.almacen.pop()
        if caja is None:
            return False, "[!] Error: El almacén está vacío (no hay cajas que retirar).", ""
        self.stats["retiradas"] += 1
        self.bitacora.registrar("POP", caja)
        nueva = self.almacen.top()
        detalle = "El almacén quedó vacío." if nueva is None else f"Nueva cima: [{nueva}]"
        return True, f"-> Caja [{caja}] retirada de la cima.", detalle

    def llega_camion(self, ident):
        if not self.fila.enqueue(ident):
            return False, (f"[!] Error: La bahía está llena "
                           f"(capacidad máxima: {self.fila.capacidad} camiones)."), ""
        self.stats["llegados"] += 1
        self.bitacora.registrar("ENQUEUE", ident)
        return True, f"-> Camión [{ident}] formado en la fila.", ""

    def despachar_camion(self):
        camion = self.fila.dequeue()
        if camion is None:
            return False, "[!] Error: No hay camiones esperando turno.", ""
        self.stats["despachados"] += 1
        self.bitacora.registrar("DEQUEUE", camion)
        siguiente = self.fila.first()
        detalle = "La fila quedó vacía." if siguiente is None else f"Próximo en el frente: [{siguiente}]"
        return True, f"-> Camión [{camion}] despachado.", detalle

    def cargar_demo(self):
        """Datos de ejemplo para presentar rápido."""
        for caja in ("Caja-101", "Caja-102", "Caja-103"):
            if caja not in self.almacen.listar():
                self.apilar_caja(caja)
        for camion in ("Camión-Alfa", "Camión-Beta", "Camión-Gamma"):
            if camion not in self.fila.listar():
                self.llega_camion(camion)


# =====================================================================
#  PARTE 4: INTERFAZ DE CONSOLA
# =====================================================================
USAR_COLORES = True      # Ponlo en False si la terminal muestra símbolos raros
ANCHO = 50
MAX_CAJAS_VISIBLES = 6
MAX_CAMIONES_VISIBLES = 4

_COLORES = {
    "verde": "\033[92m", "rojo": "\033[91m", "amarillo": "\033[93m",
    "cyan": "\033[96m", "magenta": "\033[95m", "gris": "\033[90m",
    "negrita": "\033[1m",
}
_RESET = "\033[0m"

if USAR_COLORES and os.name == "nt":
    os.system("")  # Activa los códigos ANSI en la consola de Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")  # Para los marcos ┌─┐ en Windows
except Exception:
    pass


def pintar(texto, color):
    if not USAR_COLORES:
        return texto
    return f"{_COLORES[color]}{texto}{_RESET}"


def ok(mensaje):
    print(pintar(mensaje, "verde"))


def error(mensaje):
    print(pintar(mensaje, "rojo"))


def aviso(mensaje):
    print(pintar(mensaje, "amarillo"))


def info(mensaje):
    print(pintar(mensaje, "gris"))


def mostrar_menu():
    print()
    print(pintar("=" * ANCHO, "cyan"))
    print(pintar("SISTEMA DE DESPACHO Y ALMACÉN".center(ANCHO), "negrita"))
    print(pintar("=" * ANCHO, "cyan"))
    opciones = [
        ("1", "[PILA]", "amarillo", "Apilar caja (push)"),
        ("2", "[PILA]", "amarillo", "Retirar caja de la cima (pop)"),
        ("3", "[COLA]", "magenta", "Llega camión a la fila (enqueue)"),
        ("4", "[COLA]", "magenta", "Despachar primer camión (dequeue)"),
        ("5", "", "", "Ver estado del almacén y camiones"),
        ("6", "", "", "Salir del programa"),
    ]
    for numero, etiqueta, color, texto in opciones:
        if etiqueta:
            print(f"{numero}. {pintar(etiqueta, color)} {texto}")
        else:
            print(f"{numero}. {texto}")
    print(pintar("-" * ANCHO, "gris"))


def dibujar_pila(almacen):
    cajas = almacen.listar()  # De la cima a la base
    cap = "" if almacen.capacidad is None else f"  {len(almacen)}/{almacen.capacidad}"
    print(pintar("  ALMACÉN (PILA / LIFO)" + cap, "amarillo"))
    if not cajas:
        print("  (almacén vacío)")
        print("  └" + "─" * 12 + "┘ BASE")
        return
    visibles = cajas[:MAX_CAJAS_VISIBLES]
    ocultas = len(cajas) - len(visibles)
    ancho = max(12, max(len(c) for c in visibles) + 2)
    print("  ┌" + "─" * ancho + "┐")
    for i, caja in enumerate(visibles):
        marca = pintar("  ← CIMA", "verde") if i == 0 else ""
        print("  │" + caja.center(ancho) + "│" + marca)
        if i < len(visibles) - 1:
            print("  ├" + "─" * ancho + "┤")
    if ocultas > 0:
        print("  ├" + "─" * ancho + "┤")
        print("  │" + f"⋮ +{ocultas} más".center(ancho) + "│")
    print("  └" + "─" * ancho + "┘ BASE")


def dibujar_fila(fila):
    camiones = fila.listar()  # Del frente al fin
    cap = "" if fila.capacidad is None else f"  {len(fila)}/{fila.capacidad}"
    print(pintar("  BAHÍA DE CAMIONES (COLA / FIFO)" + cap, "magenta"))
    if not camiones:
        print("  FRENTE → (sin camiones) ← FIN")
        return
    visibles = camiones[:MAX_CAMIONES_VISIBLES]
    ocultos = len(camiones) - len(visibles)
    cuerpo = " → ".join(f"[{c}]" for c in visibles)
    if ocultos > 0:
        cuerpo += f" → … +{ocultos} más"
    print(f"  FRENTE → {cuerpo} ← FIN")


def mostrar_estado(centro):
    print()
    dibujar_pila(centro.almacen)
    print()
    dibujar_fila(centro.fila)
    print()
    print(pintar("-" * ANCHO, "gris"))
    print("ESTADO ACTUAL:")
    print(f"- Cajas apiladas (Cima -> Base): {centro.almacen.listar()}")
    print(f"- Fila de camiones (Frente -> Fin): {centro.fila.listar()}")
    print(pintar("-" * ANCHO, "gris"))
    s = centro.stats
    info(f"Resumen: {s['apiladas']} apiladas · {s['retiradas']} retiradas · "
         f"{s['llegados']} camiones llegados · {s['despachados']} despachados")
    registros = centro.bitacora.ultimas(5)
    if registros:
        info("Últimas operaciones:")
        for hora, tipo, detalle in registros:
            info(f"  {hora}  {tipo:<8} {detalle}")


def despedida():
    print()
    print(pintar("=" * ANCHO, "cyan"))
    print("Gracias por usar el Sistema de Despacho y Almacén. ¡Hasta pronto!".center(ANCHO))
    print(pintar("=" * ANCHO, "cyan"))


def mostrar_resultado(resultado):
    exito, mensaje, detalle = resultado
    (ok if exito else error)(mensaje)
    if detalle:
        info("   " + detalle)


def ejecutar_cli(demo=False):
    centro = CentroDistribucion()
    if demo:
        centro.cargar_demo()
    try:
        while True:
            mostrar_menu()
            opcion = pedir_opcion(1, 6)
            if opcion is None:
                continue  # Entrada inválida: ya se avisó, se vuelve al menú
            print()

            if opcion == 1:
                caja = pedir_identificador("Identificador de la caja (ej. Caja-101): ",
                                           centro.almacen.listar())
                if caja is not None:
                    mostrar_resultado(centro.apilar_caja(caja))
            elif opcion == 2:
                mostrar_resultado(centro.retirar_caja())
            elif opcion == 3:
                camion = pedir_identificador("Placa o identificador del camión (ej. Camión-Alfa): ",
                                             centro.fila.listar())
                if camion is not None:
                    mostrar_resultado(centro.llega_camion(camion))
            elif opcion == 4:
                mostrar_resultado(centro.despachar_camion())
            elif opcion == 5:
                mostrar_estado(centro)
            elif opcion == 6:
                if len(centro.almacen) or len(centro.fila):
                    aviso(f"Aún quedan {len(centro.almacen)} caja(s) y {len(centro.fila)} camión(es).")
                    if not confirmar("¿Salir de todos modos? (s/n): "):
                        continue
                break
    except (KeyboardInterrupt, EOFError):
        pass  # Ctrl+C / Ctrl+D: salida limpia, sin traceback
    despedida()


# =====================================================================
#  PARTE 5B: PRUEBAS AUTOMÁTICAS (recorren el checklist del profesor)
# =====================================================================
def _simular_cli(entradas):
    """Ejecuta la consola con entradas simuladas y devuelve todo lo que imprimió."""
    global USAR_COLORES
    previo, USAR_COLORES = USAR_COLORES, False
    iterador = iter(entradas)

    def input_falso(prompt=""):
        print(prompt, end="")
        try:
            return next(iterador)
        except StopIteration:
            raise EOFError

    original, builtins.input = builtins.input, input_falso
    salida = io.StringIO()
    try:
        with contextlib.redirect_stdout(salida):
            ejecutar_cli()
    finally:
        builtins.input = original
        USAR_COLORES = previo
    return salida.getvalue()


def ejecutar_pruebas():
    resultados = []

    def comprobar(nombre, condicion):
        resultados.append((nombre, bool(condicion)))

    # --- Checklist del profesor ---------------------------------------
    c = CentroDistribucion()
    c.apilar_caja("Caja 1")
    c.apilar_caja("Caja 2")
    comprobar("Prueba LIFO (Pila): sale primero Caja 2", "[Caja 2]" in c.retirar_caja()[1])

    c = CentroDistribucion()
    c.llega_camion("Camión A")
    c.llega_camion("Camión B")
    comprobar("Prueba FIFO (Cola): sale primero Camión A", "[Camión A]" in c.despachar_camion()[1])

    c = CentroDistribucion()
    r1, r2 = c.retirar_caja(), c.despachar_camion()
    comprobar("Vaciado: pop con pila vacía avisa sin romper",
              not r1[0] and r1[1] == "[!] Error: El almacén está vacío (no hay cajas que retirar).")
    comprobar("Vaciado: dequeue con cola vacía avisa sin romper",
              not r2[0] and r2[1] == "[!] Error: No hay camiones esperando turno.")

    salida = _simular_cli(["abc", "9", "", "-1", "1.5", "2", "4", "6"])
    comprobar("Control de flujo: entradas inválidas vuelven al menú",
              salida.count("Seleccione una opción") == 8 and "Hasta pronto" in salida)

    salida = _simular_cli(["1", "Caja 1", "1", "Caja 2", "2", "3", "Camión A", "3", "Camión B",
                           "4", "6", "s"])
    comprobar("Consola completa: LIFO y FIFO por menú",
              "-> Caja [Caja 2] retirada de la cima." in salida
              and "-> Camión [Camión A] despachado." in salida)

    # --- Pruebas extra --------------------------------------------------
    comprobar("Encapsulación: no hay acceso directo a la lista interna",
              not hasattr(Stack(), "datos") and not hasattr(Queue(), "datos"))
    comprobar("Validación: identificador vacío", validar_identificador("   ")[1] is not None)
    comprobar("Validación: identificador demasiado largo",
              validar_identificador("x" * (MAX_LONGITUD_ID + 1))[1] is not None)
    comprobar("Validación: símbolos no permitidos", validar_identificador("Caja<1>")[1] is not None)
    comprobar("Validación: solo símbolos", validar_identificador("---")[1] is not None)
    comprobar("Validación: espacios y acentos son válidos",
              validar_identificador("  Camión   A ") == ("Camión A", None, False))
    comprobar("Validación: detecta duplicados sin importar mayúsculas",
              validar_identificador("caja 1", ["Caja 1"])[2] is True)

    c = CentroDistribucion()
    llenado = [c.apilar_caja(f"C{i}")[0] for i in range(CAPACIDAD_ALMACEN + 1)]
    comprobar("Capacidad: el almacén rechaza la caja sobrante",
              llenado.count(True) == CAPACIDAD_ALMACEN and llenado[-1] is False)
    llenado = [c.llega_camion(f"T{i}")[0] for i in range(CAPACIDAD_BAHIA + 1)]
    comprobar("Capacidad: la bahía rechaza el camión sobrante",
              llenado.count(True) == CAPACIDAD_BAHIA and llenado[-1] is False)

    c = CentroDistribucion()
    c.cargar_demo()
    c.retirar_caja()
    c.despachar_camion()
    comprobar("Estadísticas e historial se actualizan",
              c.stats == {"apiladas": 3, "retiradas": 1, "llegados": 3, "despachados": 1}
              and len(c.bitacora.ultimas(50)) == 8)

    # --- Reporte ----------------------------------------------------------
    print("\nPRUEBAS AUTOMÁTICAS")
    print("=" * 60)
    for nombre, paso in resultados:
        print(f"[{'OK' if paso else 'FALLO'}] {nombre}")
    fallos = sum(1 for _, paso in resultados if not paso)
    print("=" * 60)
    print(f"{len(resultados) - fallos}/{len(resultados)} pruebas correctas")
    sys.exit(1 if fallos else 0)


# =====================================================================
#  ARRANQUE
# =====================================================================
def main():
    args = sys.argv[1:]
    if "--test" in args:
        ejecutar_pruebas()
        return
    ejecutar_cli(demo="--demo" in args)


if __name__ == "__main__":
    main()
