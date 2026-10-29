"""
SISTEMA DE DESPACHO Y ALMACÉN  -  Simulador de Pilas (LIFO) y Colas (FIFO)

Uso:
    python despacho.py            -> consola (modo de evaluación del profesor)
    python despacho.py --gui      -> ventana premium con efecto glass
    python despacho.py --demo     -> arranca con datos de ejemplo (combinable)
    python despacho.py --test     -> pruebas automáticas del checklist

Estructura del archivo (una sección por integrante):
    PARTE 1  Clase Stack (pila)
    PARTE 2  Clase Queue (cola)
    PARTE 3  Validaciones de entrada
    PARTE 5A Bitácora (historial) y estadísticas
    PARTE 4  Interfaz (consola + ventana glass) y bucle principal
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

try:
    import tkinter as tk
    from tkinter import font as tkfont, messagebox
except ImportError:          # Sin tkinter solo funciona el modo consola
    tk = None

# ---------------------------------------------------------------------
#  CONFIGURACIÓN GENERAL
# ---------------------------------------------------------------------
MODO_POR_DEFECTO = "cli"     # "cli" (consola) o "gui" (ventana)
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
#  PARTE 4: LÓGICA CENTRAL (la comparten la consola y la ventana)
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
#  PARTE 4: VENTANA PREMIUM "GLASS"  (tkinter, sin librerías externas)
#
#  tkinter no tiene transparencia ni desenfoque reales, así que el efecto
#  vidrio esmerilado se "hornea" en una imagen de fondo: se genera un
#  degradado con luces de colores y, encima, los paneles se aclaran un poco
#  con borde luminoso. Todo lo que se mueve (cajas, camiones) se dibuja
#  encima en un Canvas.
# =====================================================================
ANCHO_V, ALTO_V = 1040, 680
ESCALA_FONDO = 2     # El fondo se calcula a media resolución y se amplía (más rápido)
RADIO_PANEL = 22

# (x, y, ancho, alto) de cada panel de vidrio
PANELES = {
    "cabecera":  (24, 20, 992, 72),
    "almacen":   (24, 108, 360, 552),
    "bahia":     (400, 108, 616, 190),
    "controles": (400, 314, 616, 170),
    "historial": (400, 500, 616, 160),
}

C_FONDO = "#0b1026"
C_TEXTO = "#f5f3ff"
C_MUTED = "#b4b0e0"
C_CYAN = "#67e8f9"
C_VIOLETA = "#a78bfa"
C_OK = "#4ade80"
C_ERR = "#fb7185"
C_AVISO = "#fbbf24"
C_CAJAS = ["#6d5dfc", "#8b5cf6", "#a855f7", "#d946ef", "#ec4899",
           "#f43f5e", "#f59e0b", "#10b981", "#06b6d4", "#3b82f6"]
C_CAMIONES = ["#22d3ee", "#a78bfa", "#f472b6", "#fbbf24", "#34d399", "#60a5fa"]
MAX_VISIBLES_FILA = 5


def _hex_a_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def aclarar(h, f):
    return "#%02x%02x%02x" % tuple(int(c + (255 - c) * f) for c in _hex_a_rgb(h))


def recortar(texto, maximo):
    return texto if len(texto) <= maximo else texto[:maximo - 1] + "…"


def rrect(canvas, x1, y1, x2, y2, r, **opciones):
    """Rectángulo con esquinas redondeadas."""
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    puntos = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
              x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(puntos, smooth=True, **opciones)


def generar_fondo_filas(ancho=ANCHO_V, alto=ALTO_V, esc=ESCALA_FONDO):
    """
    Genera el fondo con paneles de vidrio. Devuelve una lista de filas,
    cada fila es una lista de colores '#rrggbb' (a resolución 1/esc).
    """
    w, h = ancho // esc, alto // esc
    base_a, base_b = (8, 10, 30), (34, 16, 68)
    # (centro x, centro y, radio, color RGB, fuerza)
    orbes = [
        (160, 80, 380, (124, 58, 237), 0.95),    # violeta
        (900, 620, 400, (8, 145, 178), 0.55),    # turquesa
        (820, 110, 280, (236, 72, 153), 0.55),   # rosa
        (260, 640, 300, (59, 130, 246), 0.50),   # azul
    ]
    datos = []
    for cx, cy, radio, color, fuerza in orbes:
        k = 4.0 / (radio * radio)
        dx2 = [(px * esc - cx) ** 2 for px in range(w)]
        dy2 = [(py * esc - cy) ** 2 for py in range(h)]
        datos.append((k, dx2, dy2, color, fuerza * 0.85))

    pix = []
    for py in range(h):
        ty = py * esc / alto
        fila = []
        for px in range(w):
            t = 0.4 * (px * esc / ancho) + 0.6 * ty
            r = base_a[0] + (base_b[0] - base_a[0]) * t
            g = base_a[1] + (base_b[1] - base_a[1]) * t
            b = base_a[2] + (base_b[2] - base_a[2]) * t
            for k, dx2, dy2, col, fz in datos:
                f = 1.0 / (1.0 + k * (dx2[px] + dy2[py]))
                f = f * f * fz
                r += col[0] * f
                g += col[1] * f
                b += col[2] * f
            fila.append([r, g, b])
        pix.append(fila)

    # Paneles de vidrio: se aclara el fondo + brillo en el borde
    for x, y, pw, ph in PANELES.values():
        rad = RADIO_PANEL
        for py in range(max(0, y // esc - 2), min(h, (y + ph) // esc + 3)):
            ly = py * esc - y
            for px in range(max(0, x // esc - 2), min(w, (x + pw) // esc + 3)):
                lx = px * esc - x
                qx = abs(lx - pw / 2) - (pw / 2 - rad)
                qy = abs(ly - ph / 2) - (ph / 2 - rad)
                ox, oy = max(qx, 0.0), max(qy, 0.0)
                d = (ox * ox + oy * oy) ** 0.5 + min(max(qx, qy), 0.0) - rad
                cob = 0.5 - d / esc
                if cob <= 0:
                    continue
                cob = min(cob, 1.0)
                rel = min(max(ly / ph, 0.0), 1.0)
                cuerpo = 0.09 + 0.07 * (1.0 - rel)             # brillo superior
                borde = max(1.0 - abs(d + esc * 0.7) / (esc * 1.3), 0.0)
                borde *= 0.34 * (1.0 - 0.5 * rel)
                a = (cuerpo + borde) * cob
                p = pix[py][px]
                p[0] += (255 - p[0]) * a
                p[1] += (255 - p[1]) * a
                p[2] += (255 - p[2]) * a

    return [["#%02x%02x%02x" % (min(255, int(p[0])), min(255, int(p[1])), min(255, int(p[2])))
             for p in fila] for fila in pix]


def crear_imagen_fondo():
    filas = generar_fondo_filas()
    imagen = tk.PhotoImage(width=len(filas[0]), height=len(filas))
    imagen.put(" ".join("{" + " ".join(fila) + "}" for fila in filas))
    return imagen.zoom(ESCALA_FONDO, ESCALA_FONDO)


class VentanaGlass:
    def __init__(self, demo=False):
        self.centro = CentroDistribucion()
        if demo:
            self.centro.cargar_demo()
        self.root = tk.Tk()
        self.root.title("Sistema de Despacho y Almacén")
        self.root.configure(bg=C_FONDO)
        self.root.resizable(False, False)
        x = max(0, (self.root.winfo_screenwidth() - ANCHO_V) // 2)
        y = max(0, (self.root.winfo_screenheight() - ALTO_V) // 2 - 20)
        self.root.geometry(f"{ANCHO_V}x{ALTO_V}+{x}+{y}")

        familias = set(tkfont.families(self.root))
        self.fuente = self._elegir(familias, ["Segoe UI Variable Display", "Segoe UI", "SF Pro Display",
                                              "Helvetica Neue", "Helvetica", "DejaVu Sans", "Arial"])
        self.mono = self._elegir(familias, ["Cascadia Mono", "Consolas", "Menlo",
                                            "DejaVu Sans Mono", "Courier New", "Courier"])
        self._gen = 0            # Se incrementa en cada redibujado (invalida animaciones viejas)
        self._toast_id = None

        self.canvas = tk.Canvas(self.root, width=ANCHO_V, height=ALTO_V,
                                bd=0, highlightthickness=0, bg=C_FONDO)
        self.canvas.pack()
        self.fondo = crear_imagen_fondo()      # Guardar la referencia evita que se borre
        self.canvas.create_image(0, 0, image=self.fondo, anchor="nw")

        self._construir_estatico()
        self.redibujar()

    # ---------- utilidades ----------
    @staticmethod
    def _elegir(disponibles, candidatas):
        for nombre in candidatas:
            if nombre in disponibles:
                return nombre
        return candidatas[-1]

    def _f(self, tam, negrita=False):
        return (self.fuente, -tam, "bold") if negrita else (self.fuente, -tam)

    def _boton(self, x1, y1, x2, y2, texto, color, comando, tag, tam=14):
        c = self.canvas
        hover = aclarar(color, 0.20)
        forma = rrect(c, x1, y1, x2, y2, 12, fill=color, outline=aclarar(color, 0.40),
                      width=1, tags=(tag,))
        c.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=texto, fill="#ffffff",
                      font=self._f(tam, True), tags=(tag,))
        c.tag_bind(tag, "<Enter>", lambda e: (c.itemconfig(forma, fill=hover), c.config(cursor="hand2")))
        c.tag_bind(tag, "<Leave>", lambda e: (c.itemconfig(forma, fill=color), c.config(cursor="")))
        c.tag_bind(tag, "<Button-1>", lambda e: comando())

    def _campo(self, x, y, ancho):
        c = self.canvas
        forma = rrect(c, x, y, x + ancho, y + 36, 12, fill="#16123a", outline="#5b54b0", width=1)
        entrada = tk.Entry(self.root, font=self._f(14), bg="#16123a", fg=C_TEXTO,
                           insertbackground=C_TEXTO, relief="flat", bd=0, highlightthickness=0,
                           selectbackground="#6d5dfc", selectforeground="#ffffff")
        c.create_window(x + 14, y + 18, window=entrada, anchor="w", width=ancho - 28, height=24)
        entrada.bind("<FocusIn>", lambda e: c.itemconfig(forma, outline=C_CYAN))
        entrada.bind("<FocusOut>", lambda e: c.itemconfig(forma, outline="#5b54b0"))
        return entrada

    def _titulo_panel(self, clave, titulo, subtitulo, color):
        x, y, w, h = PANELES[clave]
        self.canvas.create_text(x + 26, y + 30, text=titulo, anchor="w", fill=C_TEXTO, font=self._f(16, True))
        if subtitulo:
            self.canvas.create_text(x + 26, y + 52, text=subtitulo, anchor="w", fill=color, font=self._f(12))

    # ---------- elementos fijos ----------
    def _construir_estatico(self):
        c = self.canvas
        c.create_text(52, 46, text="Centro de Despacho", anchor="w", fill=C_TEXTO, font=self._f(24, True))
        c.create_text(52, 72, text="Simulador de Pilas (LIFO) y Colas (FIFO)", anchor="w",
                      fill=C_MUTED, font=self._f(12))

        self._titulo_panel("almacen", "ALMACÉN", "Pila · LIFO", C_VIOLETA)
        self._titulo_panel("bahia", "BAHÍA DE CAMIONES", "Cola · FIFO", C_CYAN)
        self._titulo_panel("controles", "OPERACIONES", "", C_MUTED)
        self._titulo_panel("historial", "HISTORIAL", "", C_MUTED)

        # Mensaje de estado (esquina del panel de operaciones)
        cx, cy, cw, ch = PANELES["controles"]
        self.item_mensaje = c.create_text(cx + cw - 26, cy + 30, anchor="e", text="Listo para operar",
                                          fill=C_MUTED, font=self._f(12), width=420, justify="right")

        # Grupo de cajas (izquierda) y de camiones (derecha)
        gx_izq, gx_der, ancho_g = cx + 24, cx + 320, 272
        c.create_text(gx_izq, cy + 62, text="CAJA", anchor="w", fill=C_MUTED, font=self._f(11, True))
        c.create_text(gx_der, cy + 62, text="CAMIÓN", anchor="w", fill=C_MUTED, font=self._f(11, True))
        self.ent_caja = self._campo(gx_izq, cy + 72, ancho_g)
        self.ent_camion = self._campo(gx_der, cy + 72, ancho_g)
        self.ent_caja.bind("<Return>", lambda e: self.apilar())
        self.ent_camion.bind("<Return>", lambda e: self.llega_camion())

        yb = cy + 118
        self._boton(gx_izq, yb, gx_izq + 130, yb + 36, "Apilar", "#6d5dfc", self.apilar, "b_push")
        self._boton(gx_izq + 142, yb, gx_izq + 272, yb + 36, "Retirar", "#e0457b", self.retirar, "b_pop")
        self._boton(gx_der, yb, gx_der + 130, yb + 36, "Llega camión", "#0ea5c6", self.llega_camion, "b_enq")
        self._boton(gx_der + 142, yb, gx_der + 272, yb + 36, "Despachar", "#d98a0b", self.despachar, "b_deq")

        # Botones pequeños del historial
        hx, hy, hw, hh = PANELES["historial"]
        self._boton(hx + hw - 26 - 72, hy + 16, hx + hw - 26, hy + 40, "Reiniciar", "#3b3680",
                    self.reiniciar, "b_reset", 12)
        self._boton(hx + hw - 26 - 72 - 14 - 66, hy + 16, hx + hw - 26 - 72 - 14, hy + 40, "Demo",
                    "#3b3680", self.cargar_demo, "b_demo", 12)

        self.ent_caja.focus_set()

    # ---------- elementos dinámicos ----------
    def redibujar(self, evento=None):
        self._gen += 1
        self.canvas.delete("dyn")
        self._dibujar_cabecera()
        self._dibujar_pila(evento)
        self._dibujar_fila(evento)
        self._dibujar_historial()

    def _dibujar_cabecera(self):
        c = self.canvas
        columnas = [("apiladas", "APILADAS"), ("retiradas", "RETIRADAS"),
                    ("llegados", "LLEGADOS"), ("despachados", "DESPACHADOS")]
        for i, (clave, etiqueta) in enumerate(columnas):
            cx = 573 + i * 118
            c.create_text(cx, 46, text=str(self.centro.stats[clave]), fill=C_TEXTO,
                          font=self._f(24, True), tags="dyn")
            c.create_text(cx, 72, text=etiqueta, fill=C_MUTED, font=self._f(10, True), tags="dyn")

    def _dibujar_caja(self, x1, y1, x2, y2, color, texto, tags):
        c = self.canvas
        rrect(c, x1, y1, x2, y2, 9, fill=color, outline=aclarar(color, 0.45), width=1, tags=tags)
        c.create_line(x1 + 12, y1 + 4, x2 - 12, y1 + 4, fill=aclarar(color, 0.55), tags=tags)
        c.create_text((x1 + x2) / 2, (y1 + y2) / 2 + 1, text=recortar(texto, 22),
                      fill="#ffffff", font=self._f(13, True), tags=tags)

    def _dibujar_pila(self, evento):
        c = self.canvas
        x, y, w, h = PANELES["almacen"]
        almacen = self.centro.almacen
        cajas = almacen.listar()                      # cima -> base
        n = len(cajas)
        cap = almacen.capacidad or max(n, 10)
        c.create_text(x + w - 26, y + 36, text=f"{n}/{cap}", anchor="e", fill=C_TEXTO,
                      font=self._f(22, True), tags="dyn")
        c.create_text(x + w - 26, y + 58, text="CAJAS", anchor="e", fill=C_MUTED,
                      font=self._f(10, True), tags="dyn")

        piso, techo = y + h - 40, y + 78
        paso = min(44.0, (piso - techo) / cap)
        alto = paso - 6
        x1 = x + (w - 200) / 2
        x2 = x1 + 200

        def borde_inferior(i):                         # i = posición desde la base
            return piso - 3 - i * paso

        for i in range(cap):                           # Huecos libres (guía visual)
            rrect(c, x1, borde_inferior(i) - alto, x2, borde_inferior(i), 9,
                  fill="", outline="#4a4590", dash=(3, 4), tags="dyn")
        c.create_line(x1 - 20, piso, x2 + 20, piso, fill="#8f89e6", width=2, tags="dyn")
        c.create_text((x1 + x2) / 2, piso + 16, text="BASE", fill=C_MUTED,
                      font=self._f(10, True), tags="dyn")

        if n == 0:
            c.create_text((x1 + x2) / 2, (techo + piso) / 2, text="Almacén vacío", fill=C_MUTED,
                          font=self._f(14), tags="dyn")

        for i in range(n):
            texto = cajas[n - 1 - i]
            es_cima = (i == n - 1)
            nueva = es_cima and evento and evento[0] == "push"
            tags = ("dyn", "anim_caja") if nueva else ("dyn",)
            self._dibujar_caja(x1, borde_inferior(i) - alto, x2, borde_inferior(i),
                               C_CAJAS[i % len(C_CAJAS)], texto, tags)
            if es_cima:
                c.create_text(x2 + 12, borde_inferior(i) - alto / 2, text="← CIMA", anchor="w",
                              fill=C_CYAN, font=self._f(11, True), tags="dyn")

        if evento and evento[0] == "push":
            self._animar("anim_caja", 0, 70)
        elif evento and evento[0] == "pop":
            _, i, texto = evento                       # La caja retirada sube y desaparece
            self._dibujar_caja(x1, borde_inferior(i) - alto, x2, borde_inferior(i),
                               C_CAJAS[i % len(C_CAJAS)], texto, ("dyn", "fantasma"))
            self._animar("fantasma", 0, -70, entrada=False, borrar=True)

    def _dibujar_camion(self, x, y, w, h, nombre, primero, tags):
        c = self.canvas
        color = C_CAMIONES[sum(map(ord, nombre)) % len(C_CAMIONES)]
        rrect(c, x, y, x + w, y + h, 14, fill="#241f55",
              outline=C_CYAN if primero else "#6d65c9", width=2 if primero else 1, tags=tags)
        rrect(c, x + 16, y + 14, x + 56, y + 42, 5, fill=color, outline=aclarar(color, 0.4), tags=tags)
        c.create_polygon(x + 58, y + 22, x + 70, y + 22, x + 80, y + 32, x + 80, y + 42, x + 58, y + 42,
                         fill=aclarar(color, 0.25), outline=aclarar(color, 0.5), tags=tags)
        c.create_polygon(x + 62, y + 25, x + 69, y + 25, x + 75, y + 32, x + 62, y + 32,
                         fill="#cffafe", outline="", tags=tags)
        for rx in (x + 26, x + 66):
            c.create_oval(rx, y + 38, rx + 12, y + 50, fill="#0f0d24", outline="#e0e7ff",
                          width=2, tags=tags)
        c.create_text(x + w / 2, y + h - 16, text=recortar(nombre, 12), fill="#ffffff",
                      font=self._f(11, True), tags=tags)

    def _dibujar_fila(self, evento):
        c = self.canvas
        x, y, w, h = PANELES["bahia"]
        fila = self.centro.fila
        camiones = fila.listar()                       # frente -> fin
        n = len(camiones)
        cap = fila.capacidad or max(n, 8)
        c.create_text(x + w - 26, y + 36, text=f"{n}/{cap}", anchor="e", fill=C_TEXTO,
                      font=self._f(22, True), tags="dyn")
        c.create_text(x + w - 26, y + 58, text="CAMIONES", anchor="e", fill=C_MUTED,
                      font=self._f(10, True), tags="dyn")
        if n == 0:
            c.create_text(x + w / 2, y + 124, text="Sin camiones en espera", fill=C_MUTED,
                          font=self._f(14), tags="dyn")
            return

        visibles = camiones if n <= MAX_VISIBLES_FILA else camiones[:MAX_VISIBLES_FILA - 1]
        ocultos = n - len(visibles)
        ancho_t, sep, alto_t = 98, 12, 84
        x0, y0 = x + 24, y + 72
        saliendo = evento and evento[0] == "deq"

        for i, nombre in enumerate(visibles):
            entra = evento and evento[0] == "enq" and i == n - 1
            tags = ["dyn"]
            if entra:
                tags.append("anim_camion")
            if saliendo:
                tags.append("anim_cola")
            self._dibujar_camion(x0 + i * (ancho_t + sep), y0, ancho_t, alto_t, nombre, i == 0, tuple(tags))

        ultimo_cx = x0 + (len(visibles) - 1) * (ancho_t + sep) + ancho_t / 2
        if ocultos > 0:
            bx = x0 + len(visibles) * (ancho_t + sep)
            tags = ("dyn", "anim_cola") if saliendo else ("dyn",)
            rrect(c, bx, y0, bx + 60, y0 + alto_t, 14, fill="#241f55", outline="#6d65c9", tags=tags)
            c.create_text(bx + 30, y0 + alto_t / 2, text=f"+{ocultos}", fill=C_TEXTO,
                          font=self._f(18, True), tags=tags)
            ultimo_cx = bx + 30
        c.create_text(x0 + ancho_t / 2, y0 + alto_t + 14, text="FRENTE", fill=C_CYAN,
                      font=self._f(10, True), tags="dyn")
        c.create_text(ultimo_cx, y0 + alto_t + 14, text="FIN", fill=C_MUTED,
                      font=self._f(10, True), tags="dyn")

        if evento and evento[0] == "enq" and n <= MAX_VISIBLES_FILA:
            self._animar("anim_camion", 140, 0)
        elif saliendo:
            self._animar("anim_cola", ancho_t + sep, 0)

    def _dibujar_historial(self):
        c = self.canvas
        x, y, w, h = PANELES["historial"]
        registros = self.centro.bitacora.ultimas(5)
        if not registros:
            c.create_text(x + 26, y + 70, text="Aún no hay operaciones", anchor="w", fill=C_MUTED,
                          font=self._f(13), tags="dyn")
            return
        colores = {"PUSH": C_VIOLETA, "POP": C_ERR, "ENQUEUE": C_CYAN, "DEQUEUE": C_AVISO}
        for i, (hora, tipo, detalle) in enumerate(reversed(registros)):   # La más reciente arriba
            yy = y + 66 + i * 20
            c.create_text(x + 26, yy, text=hora, anchor="w", fill=C_MUTED,
                          font=(self.mono, -12), tags="dyn")
            c.create_text(x + 100, yy, text=tipo, anchor="w", fill=colores.get(tipo, C_TEXTO),
                          font=(self.mono, -12, "bold"), tags="dyn")
            c.create_text(x + 190, yy, text=recortar(detalle, 40), anchor="w", fill=C_TEXTO,
                          font=(self.mono, -12), tags="dyn")

    # ---------- animación ----------
    def _animar(self, tag, dx, dy, entrada=True, pasos=10, ms=14, borrar=False):
        """
        entrada=True : el objeto empieza desplazado (-dx,-dy) y llega a su lugar.
        entrada=False: el objeto sale desde su lugar hacia (dx,dy) (y se borra si borrar=True).
        """
        c, gen = self.canvas, self._gen
        if entrada:
            c.move(tag, -dx, -dy)
        previo = 0.0

        def paso(i):
            nonlocal previo
            if gen != self._gen:        # Hubo otro redibujado: esta animación ya no aplica
                return
            t = i / pasos
            e = 1 - (1 - t) ** 3        # Suavizado de salida
            c.move(tag, dx * (e - previo), dy * (e - previo))
            previo = e
            if i < pasos:
                self.root.after(ms, paso, i + 1)
            elif borrar:
                c.delete(tag)

        self.root.after(ms, paso, 1)

    # ---------- mensajes ----------
    def _toast(self, mensaje, tipo):
        color = {"ok": C_OK, "error": C_ERR, "aviso": C_AVISO}.get(tipo, C_MUTED)
        self.canvas.itemconfig(self.item_mensaje, text=mensaje, fill=color)
        if self._toast_id is not None:
            self.root.after_cancel(self._toast_id)
        self._toast_id = self.root.after(6000, lambda: self.canvas.itemconfig(
            self.item_mensaje, text="Listo para operar", fill=C_MUTED))

    def _leer_identificador(self, entrada, existentes):
        limpio, err, duplicado = validar_identificador(entrada.get(), existentes)
        if err:
            self._toast(err, "error")
            entrada.focus_set()
            return None
        if duplicado and not messagebox.askyesno(
                "Identificador repetido",
                f"[{limpio}] ya existe en esta estructura.\n¿Agregarlo de todos modos?",
                parent=self.root):
            self._toast("Operación cancelada.", "aviso")
            return None
        return limpio

    # ---------- acciones de los botones ----------
    def apilar(self):
        ident = self._leer_identificador(self.ent_caja, self.centro.almacen.listar())
        if ident is None:
            return
        exito, mensaje, _ = self.centro.apilar_caja(ident)
        self._toast(mensaje, "ok" if exito else "error")
        if exito:
            self.ent_caja.delete(0, "end")
            self.redibujar(("push",))

    def retirar(self):
        antes = self.centro.almacen.listar()
        exito, mensaje, _ = self.centro.retirar_caja()
        self._toast(mensaje, "ok" if exito else "error")
        if exito:
            self.redibujar(("pop", len(antes) - 1, antes[0]))

    def llega_camion(self):
        ident = self._leer_identificador(self.ent_camion, self.centro.fila.listar())
        if ident is None:
            return
        exito, mensaje, _ = self.centro.llega_camion(ident)
        self._toast(mensaje, "ok" if exito else "error")
        if exito:
            self.ent_camion.delete(0, "end")
            self.redibujar(("enq",))

    def despachar(self):
        exito, mensaje, _ = self.centro.despachar_camion()
        self._toast(mensaje, "ok" if exito else "error")
        if exito:
            self.redibujar(("deq",))

    def cargar_demo(self):
        self.centro.cargar_demo()
        self.redibujar()
        self._toast("Datos de demostración cargados.", "aviso")

    def reiniciar(self):
        if messagebox.askyesno("Reiniciar", "Se vaciarán el almacén, la fila y el historial.\n¿Continuar?",
                               parent=self.root):
            self.centro = CentroDistribucion()
            self.redibujar()
            self._toast("Sistema reiniciado.", "aviso")

    def ejecutar(self):
        self.root.mainloop()


def iniciar_gui(demo=False):
    if tk is None:
        print("[!] Este Python no tiene tkinter. Se usará el modo consola.")
        ejecutar_cli(demo)
        return
    try:
        app = VentanaGlass(demo)
    except tk.TclError as problema:
        print(f"[!] No se pudo abrir la ventana ({problema}). Se usará el modo consola.")
        ejecutar_cli(demo)
        return
    app.ejecutar()


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
    demo = "--demo" in args
    modo = "gui" if "--gui" in args else ("cli" if "--cli" in args else MODO_POR_DEFECTO)
    if modo == "gui":
        iniciar_gui(demo)
    else:
        ejecutar_cli(demo)


if __name__ == "__main__":
    main()
