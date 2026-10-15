"""
Sistema de Control de Inventario - Miriam Atelier (versión con ventanas)
Fundamentos de Programación II - programación orientada a objetos

Pantallas: Página principal, Registrar vestido (HU04), Venta (HU05),
           Registro de mercadería (HU06), Consultar stock y Ganancias totales.

Ejecutar:  python miriam_atelier_ventana.py
(tkinter viene incluido con Python; no hay que instalar nada)
"""

import tkinter as tk
from tkinter import ttk, messagebox

TALLAS = ["S", "M", "L", "XL"]
TIPOS = ["Fiesta", "Casual"]
STOCK_BAJO = 5          # si el stock total del modelo es este número o menos, se avisa

# Colores y fuentes
MORADO = "#7B4B94"
MORADO_CLARO = "#9B6BA8"
LATERAL = "#3B2A4A"
FONDO = "#F4F1F7"
BLANCO = "#FFFFFF"
TEXTO = "#1F1B2E"
GRIS = "#6B6B7B"
VERDE = "#1E8449"
ROJO = "#C0392B"
ROJO_SUAVE = "#FADBD8"
FUENTE = ("Arial", 10)
FUENTE_NEGRITA = ("Arial", 10, "bold")


# =====================================================================
# CLASES DEL NEGOCIO (atributos privados + métodos de acceso)
# =====================================================================
class Vestido:
    def __init__(self, codigo, nombre, tipo, precio_compra, precio_venta):
        self.__codigo = codigo
        self.__nombre = nombre
        self.__tipo = tipo
        self.__precio_compra = precio_compra
        self.__precio_venta = precio_venta
        self.__stock = {}                    # stock por talla
        for talla in TALLAS:
            self.__stock[talla] = 0

    def get_codigo(self):
        return self.__codigo

    def get_nombre(self):
        return self.__nombre

    def get_tipo(self):
        return self.__tipo

    def get_precio_compra(self):
        return self.__precio_compra

    def get_precio_venta(self):
        return self.__precio_venta

    def get_stock(self, talla):
        return self.__stock[talla]

    def get_stock_total(self):
        total = 0
        for talla in TALLAS:
            total = total + self.__stock[talla]
        return total

    def tiene_stock_bajo(self):
        return self.get_stock_total() <= STOCK_BAJO

    def set_precio_compra(self, valor):
        if valor <= 0:
            raise ValueError("El precio de compra debe ser mayor que 0.")
        self.__precio_compra = valor

    def aumentar_stock(self, talla, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")
        self.__stock[talla] = self.__stock[talla] + cantidad

    def descontar_stock(self, talla, cantidad):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0.")
        if cantidad > self.__stock[talla]:
            raise ValueError("Stock insuficiente: solo hay " + str(self.__stock[talla])
                             + " unidad(es) en talla " + talla + ".")
        self.__stock[talla] = self.__stock[talla] - cantidad


class Ingreso:
    """Un ingreso de mercadería (prototipos 4 y 6)."""

    def __init__(self, id_ingreso, vestido, talla, cantidad, precio_compra):
        self.__id = id_ingreso
        self.__vestido = vestido
        self.__talla = talla
        self.__cantidad = cantidad
        self.__precio_compra = precio_compra

    def get_id(self):
        return self.__id

    def get_vestido(self):
        return self.__vestido

    def get_talla(self):
        return self.__talla

    def get_cantidad(self):
        return self.__cantidad

    def get_precio_compra(self):
        return self.__precio_compra

    def get_total(self):
        return self.__cantidad * self.__precio_compra


class Venta:
    """Una venta (prototipo 5). Guarda el costo del momento para calcular la ganancia."""

    def __init__(self, id_venta, cliente, vestido, talla, cantidad, precio_venta, costo):
        self.__id = id_venta
        self.__cliente = cliente
        self.__vestido = vestido
        self.__talla = talla
        self.__cantidad = cantidad
        self.__precio_venta = precio_venta
        self.__costo = costo

    def get_id(self):
        return self.__id

    def get_cliente(self):
        return self.__cliente

    def get_vestido(self):
        return self.__vestido

    def get_talla(self):
        return self.__talla

    def get_cantidad(self):
        return self.__cantidad

    def get_precio_venta(self):
        return self.__precio_venta

    def get_costo(self):
        return self.__costo

    def get_total(self):
        return self.__cantidad * self.__precio_venta

    def get_costo_total(self):
        return self.__cantidad * self.__costo

    def get_ganancia(self):
        return self.get_total() - self.get_costo_total()


class Inventario:
    """Guarda las listas y contiene la lógica del negocio."""

    def __init__(self):
        self.__vestidos = []
        self.__ventas = []
        self.__ingresos = []

    def get_vestidos(self):
        return self.__vestidos

    def get_ventas(self):
        return self.__ventas

    def get_ingresos(self):
        return self.__ingresos

    def buscar_por_nombre(self, nombre):
        for v in self.__vestidos:
            if v.get_nombre() == nombre:
                return v
        return None

    def registrar_vestido(self, nombre, tipo, precio_compra, precio_venta):
        if nombre == "":
            raise ValueError("El nombre del producto no puede estar vacío.")
        if precio_compra <= 0 or precio_venta <= 0:
            raise ValueError("Los precios deben ser mayores que 0.")
        if precio_venta < precio_compra:
            raise ValueError("El precio de venta no puede ser menor al de compra.")
        for v in self.__vestidos:
            if v.get_nombre().lower() == nombre.lower():
                raise ValueError("Ya existe un vestido con ese nombre.")
        codigo = "VES-" + str(len(self.__vestidos) + 1).zfill(3)
        vestido = Vestido(codigo, nombre, tipo, precio_compra, precio_venta)
        self.__vestidos.append(vestido)
        return vestido

    def registrar_ingreso(self, vestido, talla, cantidad, precio_compra):
        vestido.aumentar_stock(talla, cantidad)          # valida la cantidad
        vestido.set_precio_compra(precio_compra)         # el costo pasa a ser el último pagado
        id_ingreso = "INGR-" + str(len(self.__ingresos) + 1).zfill(3)
        ingreso = Ingreso(id_ingreso, vestido.get_nombre(), talla, cantidad, precio_compra)
        self.__ingresos.append(ingreso)
        return ingreso

    def registrar_venta(self, cliente, vestido, talla, cantidad):
        if cliente == "":
            raise ValueError("El nombre del cliente no puede estar vacío.")
        vestido.descontar_stock(talla, cantidad)         # valida cantidad y stock
        id_venta = "VT-" + str(len(self.__ventas) + 1).zfill(3)
        venta = Venta(id_venta, cliente, vestido.get_nombre(), talla, cantidad,
                      vestido.get_precio_venta(), vestido.get_precio_compra())
        self.__ventas.append(venta)
        return venta

    def total_vendido(self):
        total = 0
        for v in self.__ventas:
            total = total + v.get_total()
        return total

    def total_costo_vendido(self):
        total = 0
        for v in self.__ventas:
            total = total + v.get_costo_total()
        return total

    def total_ganancia(self):
        return self.total_vendido() - self.total_costo_vendido()

    def total_invertido(self):
        total = 0
        for i in self.__ingresos:
            total = total + i.get_total()
        return total

    def total_unidades(self):
        total = 0
        for v in self.__vestidos:
            total = total + v.get_stock_total()
        return total

    def vestidos_con_stock_bajo(self):
        lista = []
        for v in self.__vestidos:
            if v.tiene_stock_bajo():
                lista.append(v)
        return lista


def cargar_datos_ejemplo(inv):
    """Vestidos de los prototipos para poder probar el sistema desde el inicio."""
    rojo = inv.registrar_vestido("Vestido Fiesta Rojo", "Fiesta", 85.00, 150.00)
    azul = inv.registrar_vestido("Vestido Coctel Azul", "Fiesta", 70.00, 120.00)
    gris = inv.registrar_vestido("Traje de sastre Gris", "Casual", 60.00, 110.00)
    inv.registrar_ingreso(rojo, "S", 4, 85.00)
    inv.registrar_ingreso(rojo, "M", 8, 85.00)
    inv.registrar_ingreso(rojo, "L", 5, 85.00)
    inv.registrar_ingreso(azul, "M", 6, 70.00)
    inv.registrar_ingreso(azul, "L", 2, 70.00)
    inv.registrar_ingreso(gris, "M", 7, 60.00)
    inv.registrar_ingreso(gris, "XL", 5, 60.00)


# =====================================================================
# FUNCIONES DE APOYO PARA LA INTERFAZ
# =====================================================================
def leer_decimal(texto, nombre):
    try:
        valor = float(texto.strip().replace(",", "."))
    except ValueError:
        raise ValueError("El campo '" + nombre + "' debe ser un número (ejemplo: 85.50).")
    if valor <= 0:
        raise ValueError("El campo '" + nombre + "' debe ser mayor que 0.")
    return valor


def leer_entero(texto, nombre, minimo=1):
    texto = texto.strip()
    if not texto.isdigit() or int(texto) < minimo:
        raise ValueError("El campo '" + nombre + "' debe ser un número entero mayor o igual a "
                         + str(minimo) + ".")
    return int(texto)


def dinero(valor):
    return "S/ " + format(valor, ".2f")


def crear_tabla(padre, columnas, alto=8):
    """columnas: lista de (id, texto, ancho, alineación). Devuelve (marco, tabla)."""
    marco = tk.Frame(padre, bg=FONDO)
    ids = []
    for c in columnas:
        ids.append(c[0])
    tabla = ttk.Treeview(marco, columns=ids, show="headings", height=alto)
    for ident, texto, ancho, ancla in columnas:
        tabla.heading(ident, text=texto)
        tabla.column(ident, width=ancho, minwidth=40, anchor=ancla)
    barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
    tabla.configure(yscrollcommand=barra.set)
    tabla.tag_configure("bajo", background=ROJO_SUAVE)
    tabla.pack(side="left", fill="both", expand=True)
    barra.pack(side="right", fill="y")
    return marco, tabla


def llenar_tabla(tabla, filas, etiquetas=None):
    for item in tabla.get_children():
        tabla.delete(item)
    for i in range(len(filas)):
        if etiquetas is None:
            tabla.insert("", "end", values=filas[i])
        else:
            tabla.insert("", "end", values=filas[i], tags=(etiquetas[i],))


def crear_tarjeta(padre, titulo):
    """Cuadro con un número grande. Devuelve (marco, etiqueta_del_valor)."""
    marco = tk.Frame(padre, bg=BLANCO, padx=18, pady=14,
                     highlightbackground="#DDD5E6", highlightthickness=1)
    valor = tk.Label(marco, text="0", bg=BLANCO, fg=MORADO, font=("Arial", 22, "bold"), anchor="w")
    valor.pack(fill="x")
    tk.Label(marco, text=titulo, bg=BLANCO, fg=GRIS, font=FUENTE, anchor="w").pack(fill="x")
    return marco, valor


def poner_fila(form, fila, texto, widget):
    tk.Label(form, text=texto, bg=BLANCO, fg=TEXTO, font=FUENTE, anchor="w").grid(
        row=fila, column=0, sticky="w", padx=(0, 18), pady=7)
    widget.grid(row=fila, column=1, sticky="ew", pady=7)


# =====================================================================
# PANTALLAS
# =====================================================================
class Pantalla(tk.Frame):
    """Base de todas las pantallas."""

    def __init__(self, padre, app):
        super().__init__(padre, bg=FONDO)
        self.app = app
        self.inv = app.inv
        self.mensaje = None

    def encabezado(self, titulo, subtitulo):
        tk.Label(self, text=titulo, bg=FONDO, fg=TEXTO, font=("Arial", 18, "bold"),
                 anchor="w").pack(fill="x", padx=24, pady=(20, 0))
        tk.Label(self, text=subtitulo, bg=FONDO, fg=GRIS, font=FUENTE,
                 anchor="w").pack(fill="x", padx=24, pady=(0, 12))

    def crear_mensaje(self):
        self.mensaje = tk.Label(self, text="", bg=FONDO, font=FUENTE_NEGRITA, anchor="w")
        self.mensaje.pack(fill="x", padx=24, pady=(8, 0))

    def avisar(self, texto, correcto=True):
        if correcto:
            self.mensaje.configure(text=texto, fg=VERDE)
        else:
            self.mensaje.configure(text=texto, fg=ROJO)
        self.after(5000, self.borrar_aviso)

    def borrar_aviso(self):
        self.mensaje.configure(text="")

    def actualizar(self, *args):
        pass


# ---------------------------------------------------------------- principal
class PantallaPrincipal(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Miriam Atelier", "Resumen general del inventario")

        tarjetas = tk.Frame(self, bg=FONDO)
        tarjetas.pack(fill="x", padx=24)
        self.valores = {}
        titulos = [("modelos", "Modelos registrados"), ("unidades", "Unidades en stock"),
                   ("ventas", "Ventas realizadas"), ("ganancia", "Ganancia acumulada")]
        for i in range(len(titulos)):
            tarjeta, valor = crear_tarjeta(tarjetas, titulos[i][1])
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0, 12))
            tarjetas.columnconfigure(i, weight=1)
            self.valores[titulos[i][0]] = valor

        tk.Label(self, text="Alertas de stock bajo", bg=FONDO, fg=TEXTO, font=("Arial", 12, "bold"),
                 anchor="w").pack(fill="x", padx=24, pady=(24, 6))
        self.lista_alertas = tk.Listbox(self, height=6, bd=0, font=FUENTE, bg=BLANCO,
                                        highlightthickness=1, highlightbackground="#DDD5E6",
                                        selectbackground=ROJO_SUAVE, selectforeground=TEXTO)
        self.lista_alertas.pack(fill="x", padx=24)

        tk.Label(self, text="Accesos rápidos", bg=FONDO, fg=TEXTO, font=("Arial", 12, "bold"),
                 anchor="w").pack(fill="x", padx=24, pady=(24, 6))
        botones = tk.Frame(self, bg=FONDO)
        botones.pack(fill="x", padx=24)
        accesos = [("Registrar venta", "venta"), ("Registrar mercadería", "ingreso"),
                   ("Consultar stock", "stock")]
        for texto, clave in accesos:
            ttk.Button(botones, text=texto, style="Accent.TButton",
                       command=lambda c=clave: self.app.mostrar(c)).pack(side="left", padx=(0, 10))

    def actualizar(self, *args):
        self.valores["modelos"].configure(text=str(len(self.inv.get_vestidos())))
        self.valores["unidades"].configure(text=str(self.inv.total_unidades()))
        self.valores["ventas"].configure(text=str(len(self.inv.get_ventas())))
        self.valores["ganancia"].configure(text=dinero(self.inv.total_ganancia()))
        self.lista_alertas.delete(0, "end")
        bajos = self.inv.vestidos_con_stock_bajo()
        if len(bajos) == 0:
            self.lista_alertas.insert("end", "  Todo en orden: ningún modelo con stock bajo.")
        for v in bajos:
            self.lista_alertas.insert("end", "  " + v.get_codigo() + " · " + v.get_nombre()
                                     + " — quedan " + str(v.get_stock_total()) + " unidad(es)")


# ---------------------------------------------------------------- registrar vestido (HU04)
class PantallaRegistrar(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Registro de nuevo vestido", "HU04 · Agregue un modelo al catálogo")

        self.v_nombre = tk.StringVar()
        self.v_tipo = tk.StringVar(value=TIPOS[0])
        self.v_compra = tk.StringVar()
        self.v_venta = tk.StringVar()
        self.v_talla = tk.StringVar(value=TALLAS[1])
        self.v_cantidad = tk.StringVar(value="0")

        form = tk.Frame(self, bg=BLANCO, padx=22, pady=16,
                        highlightbackground="#DDD5E6", highlightthickness=1)
        form.pack(fill="x", padx=24)
        form.columnconfigure(1, weight=1)
        poner_fila(form, 0, "Producto", ttk.Entry(form, textvariable=self.v_nombre))
        poner_fila(form, 1, "Tipo de prenda",
                   ttk.Combobox(form, textvariable=self.v_tipo, values=TIPOS, state="readonly"))
        poner_fila(form, 2, "Precio compra (S/.)", ttk.Entry(form, textvariable=self.v_compra))
        poner_fila(form, 3, "Precio venta (S/.)", ttk.Entry(form, textvariable=self.v_venta))
        poner_fila(form, 4, "Talla del stock inicial",
                   ttk.Combobox(form, textvariable=self.v_talla, values=TALLAS, state="readonly"))
        poner_fila(form, 5, "Cantidad inicial (0 = sin stock)",
                   ttk.Spinbox(form, from_=0, to=1000, textvariable=self.v_cantidad))

        botones = tk.Frame(form, bg=BLANCO)
        botones.grid(row=6, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="right", padx=(10, 0))
        ttk.Button(botones, text="Registrar", style="Accent.TButton",
                   command=self.registrar).pack(side="right")

        self.crear_mensaje()
        tk.Label(self, text="Vestidos registrados", bg=FONDO, fg=TEXTO, font=("Arial", 12, "bold"),
                 anchor="w").pack(fill="x", padx=24, pady=(12, 6))
        marco, self.tabla = crear_tabla(self, [
            ("codigo", "Código", 80, "center"), ("producto", "Producto", 220, "w"),
            ("tipo", "Tipo", 80, "center"), ("compra", "P. Compra", 90, "e"),
            ("venta", "P. Venta", 90, "e"), ("stock", "Stock total", 90, "center")], alto=6)
        marco.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def limpiar(self):
        self.v_nombre.set("")
        self.v_tipo.set(TIPOS[0])
        self.v_compra.set("")
        self.v_venta.set("")
        self.v_talla.set(TALLAS[1])
        self.v_cantidad.set("0")

    def registrar(self):
        try:
            nombre = self.v_nombre.get().strip()
            tipo = self.v_tipo.get()
            talla = self.v_talla.get()
            if tipo == "" or talla == "":
                raise ValueError("Seleccione el tipo de prenda y la talla.")
            compra = leer_decimal(self.v_compra.get(), "Precio compra")
            venta = leer_decimal(self.v_venta.get(), "Precio venta")
            cantidad = leer_entero(self.v_cantidad.get(), "Cantidad inicial", 0)
            vestido = self.inv.registrar_vestido(nombre, tipo, compra, venta)
            if cantidad > 0:
                self.inv.registrar_ingreso(vestido, talla, cantidad, compra)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return
        self.avisar("Vestido " + vestido.get_codigo() + " registrado correctamente.")
        self.limpiar()
        self.actualizar()

    def actualizar(self, *args):
        filas = []
        for v in self.inv.get_vestidos():
            filas.append((v.get_codigo(), v.get_nombre(), v.get_tipo(),
                          format(v.get_precio_compra(), ".2f"),
                          format(v.get_precio_venta(), ".2f"), v.get_stock_total()))
        llenar_tabla(self.tabla, filas)


# ---------------------------------------------------------------- venta (HU05)
class PantallaVenta(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Registrar venta de vestido", "HU05 · El stock se descuenta automáticamente")

        self.v_cliente = tk.StringVar()
        self.v_producto = tk.StringVar()
        self.v_talla = tk.StringVar(value=TALLAS[1])
        self.v_cantidad = tk.StringVar(value="1")
        self.v_precio = tk.StringVar()
        self.v_stock = tk.StringVar()
        self.v_total = tk.StringVar(value="0.00")

        form = tk.Frame(self, bg=BLANCO, padx=22, pady=16,
                        highlightbackground="#DDD5E6", highlightthickness=1)
        form.pack(fill="x", padx=24)
        form.columnconfigure(1, weight=1)
        poner_fila(form, 0, "Cliente", ttk.Entry(form, textvariable=self.v_cliente))
        self.combo_producto = ttk.Combobox(form, textvariable=self.v_producto, state="readonly")
        poner_fila(form, 1, "Producto", self.combo_producto)
        poner_fila(form, 2, "Talla",
                   ttk.Combobox(form, textvariable=self.v_talla, values=TALLAS, state="readonly"))
        poner_fila(form, 3, "Precio de venta (S/.)",
                   ttk.Entry(form, textvariable=self.v_precio, state="readonly"))
        poner_fila(form, 4, "Stock disponible",
                   ttk.Entry(form, textvariable=self.v_stock, state="readonly"))
        poner_fila(form, 5, "Cantidad",
                   ttk.Spinbox(form, from_=1, to=1000, textvariable=self.v_cantidad))
        poner_fila(form, 6, "Monto total (S/.)",
                   ttk.Entry(form, textvariable=self.v_total, state="readonly"))

        botones = tk.Frame(form, bg=BLANCO)
        botones.grid(row=7, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(botones, text="Limpiar formulario", command=self.limpiar).pack(
            side="right", padx=(10, 0))
        ttk.Button(botones, text="Registrar venta", style="Accent.TButton",
                   command=self.registrar).pack(side="right")

        # Los datos de abajo se recalculan solos cuando el usuario cambia algo
        self.v_producto.trace_add("write", self.calcular)
        self.v_talla.trace_add("write", self.calcular)
        self.v_cantidad.trace_add("write", self.calcular)

        self.crear_mensaje()
        tk.Label(self, text="Historial de ventas recientes", bg=FONDO, fg=TEXTO,
                 font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=24, pady=(12, 6))
        marco, self.tabla = crear_tabla(self, [
            ("id", "ID Venta", 80, "center"), ("cliente", "Cliente", 130, "w"),
            ("producto", "Producto", 200, "w"), ("talla", "Talla", 60, "center"),
            ("cantidad", "Cantidad", 70, "center"), ("total", "Total", 90, "e")], alto=5)
        marco.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def vestido_elegido(self):
        return self.inv.buscar_por_nombre(self.v_producto.get())

    def calcular(self, *args):
        vestido = self.vestido_elegido()
        if vestido is None:
            self.v_precio.set("")
            self.v_stock.set("")
            self.v_total.set("0.00")
            return
        precio = vestido.get_precio_venta()
        talla = self.v_talla.get()
        self.v_precio.set(format(precio, ".2f"))
        if talla in TALLAS:
            self.v_stock.set(str(vestido.get_stock(talla)))
        else:
            self.v_stock.set("")
        texto = self.v_cantidad.get().strip()
        if texto.isdigit():
            self.v_total.set(format(int(texto) * precio, ".2f"))
        else:
            self.v_total.set("0.00")

    def limpiar(self):
        self.v_cliente.set("")
        self.v_talla.set(TALLAS[1])
        self.v_cantidad.set("1")
        self.calcular()

    def registrar(self):
        vestido = self.vestido_elegido()
        if vestido is None:
            messagebox.showerror("No se pudo registrar", "Seleccione un producto.")
            return
        talla = self.v_talla.get()
        try:
            cantidad = leer_entero(self.v_cantidad.get(), "Cantidad")
            cliente = self.v_cliente.get().strip()
            if cliente == "":
                raise ValueError("El nombre del cliente no puede estar vacío.")
            if cantidad > vestido.get_stock(talla):
                raise ValueError("Stock insuficiente: solo hay " + str(vestido.get_stock(talla))
                                 + " unidad(es) en talla " + talla + ".")
            total = cantidad * vestido.get_precio_venta()
            pregunta = ("¿Registrar la venta de " + str(cantidad) + " x " + vestido.get_nombre()
                        + " (talla " + talla + ") a " + cliente + " por " + dinero(total) + "?")
            if not messagebox.askyesno("Confirmar venta", pregunta):
                return
            venta = self.inv.registrar_venta(cliente, vestido, talla, cantidad)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return
        self.avisar("Venta " + venta.get_id() + " registrada por " + dinero(venta.get_total()) + ".")
        self.limpiar()
        self.actualizar()

    def actualizar(self, *args):
        nombres = []
        for v in self.inv.get_vestidos():
            nombres.append(v.get_nombre())
        self.combo_producto.configure(values=nombres)
        if self.v_producto.get() == "" and len(nombres) > 0:
            self.v_producto.set(nombres[0])
        self.calcular()
        filas = []
        ventas = self.inv.get_ventas()
        for i in range(len(ventas) - 1, -1, -1):             # las más recientes primero
            v = ventas[i]
            filas.append((v.get_id(), v.get_cliente(), v.get_vestido(), v.get_talla(),
                          v.get_cantidad(), format(v.get_total(), ".2f")))
        llenar_tabla(self.tabla, filas)


# ---------------------------------------------------------------- mercadería (HU06)
class PantallaIngreso(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Registrar ingreso de mercadería", "HU06 · El stock se suma automáticamente")

        self.v_producto = tk.StringVar()
        self.v_talla = tk.StringVar(value=TALLAS[1])
        self.v_cantidad = tk.StringVar(value="1")
        self.v_precio = tk.StringVar()
        self.v_stock = tk.StringVar()
        self.v_total = tk.StringVar(value="0.00")

        form = tk.Frame(self, bg=BLANCO, padx=22, pady=16,
                        highlightbackground="#DDD5E6", highlightthickness=1)
        form.pack(fill="x", padx=24)
        form.columnconfigure(1, weight=1)
        self.combo_producto = ttk.Combobox(form, textvariable=self.v_producto, state="readonly")
        poner_fila(form, 0, "Producto", self.combo_producto)
        poner_fila(form, 1, "Talla",
                   ttk.Combobox(form, textvariable=self.v_talla, values=TALLAS, state="readonly"))
        poner_fila(form, 2, "Cantidad",
                   ttk.Spinbox(form, from_=1, to=1000, textvariable=self.v_cantidad))
        poner_fila(form, 3, "Precio compra (S/.)", ttk.Entry(form, textvariable=self.v_precio))
        poner_fila(form, 4, "Stock actual",
                   ttk.Entry(form, textvariable=self.v_stock, state="readonly"))
        poner_fila(form, 5, "Total de la compra (S/.)",
                   ttk.Entry(form, textvariable=self.v_total, state="readonly"))

        botones = tk.Frame(form, bg=BLANCO)
        botones.grid(row=6, column=0, columnspan=2, sticky="e", pady=(10, 0))
        ttk.Button(botones, text="Limpiar", command=self.limpiar).pack(side="right", padx=(10, 0))
        ttk.Button(botones, text="Registrar", style="Accent.TButton",
                   command=self.registrar).pack(side="right")

        self.v_producto.trace_add("write", self.al_cambiar_producto)
        self.v_talla.trace_add("write", self.calcular)
        self.v_cantidad.trace_add("write", self.calcular)
        self.v_precio.trace_add("write", self.calcular)

        self.crear_mensaje()
        tk.Label(self, text="Historial de ingresos", bg=FONDO, fg=TEXTO,
                 font=("Arial", 12, "bold"), anchor="w").pack(fill="x", padx=24, pady=(12, 6))
        marco, self.tabla = crear_tabla(self, [
            ("id", "ID Ingreso", 90, "center"), ("producto", "Producto", 200, "w"),
            ("talla", "Talla", 60, "center"), ("cantidad", "Cantidad", 70, "center"),
            ("precio", "Precio de compra", 120, "e"), ("total", "Total", 90, "e")], alto=5)
        marco.pack(fill="both", expand=True, padx=24, pady=(0, 16))

    def vestido_elegido(self):
        return self.inv.buscar_por_nombre(self.v_producto.get())

    def al_cambiar_producto(self, *args):
        vestido = self.vestido_elegido()
        if vestido is not None:
            self.v_precio.set(format(vestido.get_precio_compra(), ".2f"))   # sugiere el último precio
        self.calcular()

    def calcular(self, *args):
        vestido = self.vestido_elegido()
        talla = self.v_talla.get()
        if vestido is not None and talla in TALLAS:
            self.v_stock.set(str(vestido.get_stock(talla)))
        else:
            self.v_stock.set("")
        try:
            cantidad = int(self.v_cantidad.get().strip())
            precio = float(self.v_precio.get().strip().replace(",", "."))
            self.v_total.set(format(cantidad * precio, ".2f"))
        except ValueError:
            self.v_total.set("0.00")

    def limpiar(self):
        self.v_talla.set(TALLAS[1])
        self.v_cantidad.set("1")
        self.al_cambiar_producto()

    def registrar(self):
        vestido = self.vestido_elegido()
        if vestido is None:
            messagebox.showerror("No se pudo registrar", "Seleccione un producto.")
            return
        talla = self.v_talla.get()
        try:
            cantidad = leer_entero(self.v_cantidad.get(), "Cantidad")
            precio = leer_decimal(self.v_precio.get(), "Precio compra")
            ingreso = self.inv.registrar_ingreso(vestido, talla, cantidad, precio)
        except ValueError as error:
            messagebox.showerror("No se pudo registrar", str(error))
            return
        self.avisar("Ingreso " + ingreso.get_id() + " registrado. Nuevo stock talla " + talla
                    + ": " + str(vestido.get_stock(talla)) + ".")
        self.v_cantidad.set("1")
        self.calcular()
        self.actualizar()

    def actualizar(self, *args):
        nombres = []
        for v in self.inv.get_vestidos():
            nombres.append(v.get_nombre())
        self.combo_producto.configure(values=nombres)
        if self.v_producto.get() == "" and len(nombres) > 0:
            self.v_producto.set(nombres[0])
        self.calcular()
        filas = []
        ingresos = self.inv.get_ingresos()
        for i in range(len(ingresos) - 1, -1, -1):
            g = ingresos[i]
            filas.append((g.get_id(), g.get_vestido(), g.get_talla(), g.get_cantidad(),
                          format(g.get_precio_compra(), ".2f"), format(g.get_total(), ".2f")))
        llenar_tabla(self.tabla, filas)


# ---------------------------------------------------------------- consultar stock
class PantallaStock(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Consultar stock", "Filtre y busque; la tabla se actualiza al escribir")

        self.v_buscar = tk.StringVar()
        self.v_tipo = tk.StringVar(value="Todos")
        self.v_solo_bajo = tk.BooleanVar(value=False)

        filtros = tk.Frame(self, bg=FONDO)
        filtros.pack(fill="x", padx=24)
        tk.Label(filtros, text="Buscar:", bg=FONDO, fg=TEXTO, font=FUENTE).pack(side="left")
        ttk.Entry(filtros, textvariable=self.v_buscar, width=26).pack(side="left", padx=(6, 18))
        tk.Label(filtros, text="Tipo:", bg=FONDO, fg=TEXTO, font=FUENTE).pack(side="left")
        ttk.Combobox(filtros, textvariable=self.v_tipo, values=["Todos"] + TIPOS,
                     state="readonly", width=10).pack(side="left", padx=(6, 18))
        tk.Checkbutton(filtros, text="Solo stock bajo", variable=self.v_solo_bajo, bg=FONDO,
                       activebackground=FONDO, font=FUENTE).pack(side="left")

        self.v_buscar.trace_add("write", self.actualizar)
        self.v_tipo.trace_add("write", self.actualizar)
        self.v_solo_bajo.trace_add("write", self.actualizar)

        marco, self.tabla = crear_tabla(self, [
            ("codigo", "Código", 80, "center"), ("producto", "Producto", 210, "w"),
            ("tipo", "Tipo", 70, "center"), ("S", "S", 45, "center"), ("M", "M", 45, "center"),
            ("L", "L", 45, "center"), ("XL", "XL", 45, "center"),
            ("total", "Total", 60, "center"), ("estado", "Estado", 100, "center")], alto=12)
        marco.pack(fill="both", expand=True, padx=24, pady=(12, 6))
        self.resumen = tk.Label(self, text="", bg=FONDO, fg=GRIS, font=FUENTE, anchor="w")
        self.resumen.pack(fill="x", padx=24, pady=(0, 6))
        tk.Label(self, text="Las filas rojas son modelos con " + str(STOCK_BAJO)
                 + " unidades o menos en total.", bg=FONDO, fg=GRIS, font=FUENTE,
                 anchor="w").pack(fill="x", padx=24, pady=(0, 14))

    def actualizar(self, *args):
        texto = self.v_buscar.get().strip().lower()
        tipo = self.v_tipo.get()
        solo_bajo = self.v_solo_bajo.get()
        filas = []
        etiquetas = []
        unidades = 0
        for v in self.inv.get_vestidos():
            if texto != "" and texto not in v.get_nombre().lower() \
                    and texto not in v.get_codigo().lower():
                continue
            if tipo != "Todos" and v.get_tipo() != tipo:
                continue
            if solo_bajo and not v.tiene_stock_bajo():
                continue
            if v.tiene_stock_bajo():
                estado = "Stock bajo"
                etiquetas.append("bajo")
            else:
                estado = "OK"
                etiquetas.append("normal")
            filas.append((v.get_codigo(), v.get_nombre(), v.get_tipo(),
                          v.get_stock("S"), v.get_stock("M"), v.get_stock("L"), v.get_stock("XL"),
                          v.get_stock_total(), estado))
            unidades = unidades + v.get_stock_total()
        llenar_tabla(self.tabla, filas, etiquetas)
        self.resumen.configure(text="Mostrando " + str(len(filas)) + " modelo(s) · "
                               + str(unidades) + " unidad(es) en total")


# ---------------------------------------------------------------- ganancias
class PantallaGanancias(Pantalla):
    def __init__(self, padre, app):
        super().__init__(padre, app)
        self.encabezado("Ganancias totales", "Ganancia = precio de venta − costo, por cada unidad vendida")

        tarjetas = tk.Frame(self, bg=FONDO)
        tarjetas.pack(fill="x", padx=24)
        self.valores = {}
        titulos = [("vendido", "Total vendido"), ("costo", "Costo de lo vendido"),
                   ("ganancia", "GANANCIA TOTAL"), ("invertido", "Invertido en compras")]
        for i in range(len(titulos)):
            tarjeta, valor = crear_tarjeta(tarjetas, titulos[i][1])
            tarjeta.grid(row=0, column=i, sticky="nsew", padx=(0, 12))
            tarjetas.columnconfigure(i, weight=1)
            self.valores[titulos[i][0]] = valor

        cuerpo = tk.Frame(self, bg=FONDO)
        cuerpo.pack(fill="both", expand=True, padx=24, pady=(18, 16))
        cuerpo.columnconfigure(0, weight=3)
        cuerpo.columnconfigure(1, weight=2)
        cuerpo.rowconfigure(1, weight=1)

        tk.Label(cuerpo, text="Ganancia por venta", bg=FONDO, fg=TEXTO, font=("Arial", 12, "bold"),
                 anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 6))
        tk.Label(cuerpo, text="Ganancia por producto", bg=FONDO, fg=TEXTO,
                 font=("Arial", 12, "bold"), anchor="w").grid(
            row=0, column=1, sticky="w", pady=(0, 6), padx=(16, 0))

        marco, self.tabla = crear_tabla(cuerpo, [
            ("id", "ID Venta", 70, "center"), ("producto", "Producto", 170, "w"),
            ("cantidad", "Cant.", 50, "center"), ("venta", "P. Venta", 75, "e"),
            ("costo", "Costo", 75, "e"), ("ganancia", "Ganancia", 85, "e")], alto=10)
        marco.grid(row=1, column=0, sticky="nsew")

        self.lienzo = tk.Canvas(cuerpo, bg=BLANCO, highlightthickness=1,
                                highlightbackground="#DDD5E6", width=300, height=240)
        self.lienzo.grid(row=1, column=1, sticky="nsew", padx=(16, 0))

    def actualizar(self, *args):
        self.valores["vendido"].configure(text=dinero(self.inv.total_vendido()))
        self.valores["costo"].configure(text=dinero(self.inv.total_costo_vendido()))
        self.valores["ganancia"].configure(text=dinero(self.inv.total_ganancia()))
        self.valores["invertido"].configure(text=dinero(self.inv.total_invertido()))
        filas = []
        ventas = self.inv.get_ventas()
        for i in range(len(ventas) - 1, -1, -1):
            v = ventas[i]
            filas.append((v.get_id(), v.get_vestido(), v.get_cantidad(),
                          format(v.get_precio_venta(), ".2f"), format(v.get_costo(), ".2f"),
                          format(v.get_ganancia(), ".2f")))
        llenar_tabla(self.tabla, filas)
        self.dibujar_grafico()

    def dibujar_grafico(self):
        self.lienzo.delete("all")
        ganancias = {}
        for v in self.inv.get_ventas():
            nombre = v.get_vestido()
            ganancias[nombre] = ganancias.get(nombre, 0) + v.get_ganancia()
        if len(ganancias) == 0:
            self.lienzo.create_text(16, 24, text="Todavía no hay ventas registradas.",
                                    anchor="w", fill=GRIS, font=FUENTE)
            return
        maximo = max(ganancias.values())
        if maximo <= 0:
            maximo = 1
        y = 14
        for nombre in ganancias:
            valor = ganancias[nombre]
            largo = int(valor / maximo * 170)
            if largo < 3:
                largo = 3
            self.lienzo.create_text(10, y, text=nombre, anchor="w", fill=TEXTO, font=("Arial", 9))
            self.lienzo.create_rectangle(10, y + 12, 10 + largo, y + 30, fill=MORADO_CLARO, outline="")
            self.lienzo.create_text(16 + largo, y + 21, text=dinero(valor), anchor="w",
                                    fill=TEXTO, font=("Arial", 9, "bold"))
            y = y + 48


# =====================================================================
# VENTANA PRINCIPAL
# =====================================================================
PANTALLAS = [
    ("principal", "Página principal", PantallaPrincipal),
    ("registrar", "Registrar vestido", PantallaRegistrar),
    ("venta", "Venta", PantallaVenta),
    ("ingreso", "Registro de mercadería", PantallaIngreso),
    ("stock", "Consultar stock", PantallaStock),
    ("ganancias", "Ganancias totales", PantallaGanancias),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Miriam Atelier - Control de Inventario")
        self.geometry("1120x700")
        self.minsize(980, 620)
        self.configure(bg=FONDO)
        self.inv = Inventario()
        cargar_datos_ejemplo(self.inv)
        self.configurar_estilos()
        self.crear_menu_lateral()
        self.crear_pantallas()
        self.mostrar("principal")

    def configurar_estilos(self):
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure("Treeview", rowheight=28, font=FUENTE, background=BLANCO,
                         fieldbackground=BLANCO)
        estilo.configure("Treeview.Heading", font=FUENTE_NEGRITA, background="#E9E1F0",
                         foreground=TEXTO, relief="flat")
        estilo.map("Treeview", background=[("selected", MORADO_CLARO)],
                   foreground=[("selected", "white")])
        estilo.configure("TButton", font=FUENTE, padding=(16, 8))
        estilo.configure("Accent.TButton", font=FUENTE_NEGRITA, padding=(16, 8),
                         background=MORADO_CLARO, foreground="white", borderwidth=0)
        estilo.map("Accent.TButton", background=[("active", MORADO), ("pressed", MORADO)])
        estilo.configure("TEntry", padding=5)
        estilo.configure("TCombobox", padding=5)
        estilo.map("TEntry", fieldbackground=[("readonly", "#E9E6EE")])

    def crear_menu_lateral(self):
        lateral = tk.Frame(self, bg=LATERAL, width=220)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        tk.Label(lateral, text="Miriam\nAtelier", bg=LATERAL, fg="white",
                 font=("Arial", 20, "bold"), pady=26).pack(fill="x")
        self.botones = {}
        for clave, texto, clase in PANTALLAS:
            boton = tk.Label(lateral, text=texto, anchor="w", padx=24, pady=13, bg=LATERAL,
                             fg="white", font=("Arial", 11), cursor="hand2")
            boton.pack(fill="x")
            boton.bind("<Button-1>", lambda evento, c=clave: self.mostrar(c))
            self.botones[clave] = boton
        salir = tk.Label(lateral, text="Salir", anchor="w", padx=24, pady=13, bg=LATERAL,
                         fg="#E8B4B8", font=("Arial", 11), cursor="hand2")
        salir.pack(side="bottom", fill="x", pady=10)
        salir.bind("<Button-1>", lambda evento: self.destroy())

    def crear_pantallas(self):
        contenedor = tk.Frame(self, bg=FONDO)
        contenedor.pack(side="right", fill="both", expand=True)
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)
        self.pantallas = {}
        for clave, texto, clase in PANTALLAS:
            pantalla = clase(contenedor, self)
            pantalla.grid(row=0, column=0, sticky="nsew")
            self.pantallas[clave] = pantalla

    def mostrar(self, clave):
        for k in self.botones:
            if k == clave:
                self.botones[k].configure(bg=MORADO)
            else:
                self.botones[k].configure(bg=LATERAL)
        pantalla = self.pantallas[clave]
        pantalla.actualizar()          # cada vez que se entra, los datos se refrescan
        pantalla.tkraise()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
