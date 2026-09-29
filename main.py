import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty

DB = "negocio.db"

KV = r"""
#:import dp kivy.metrics.dp

<Btn@Button>:
    size_hint_y: None
    height: dp(48)
    font_size: "16sp"

<Title@Label>:
    font_size: "24sp"
    bold: True
    size_hint_y: None
    height: dp(55)

<TextInputBox@TextInput>:
    size_hint_y: None
    height: dp(45)
    multiline: False

<Inicio>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(15)
        spacing: dp(10)
        Title:
            text: "📊 Mi Negocio"
        Label:
            text: root.resumen
            font_size: "18sp"
        Btn:
            text: "💰 Registrar venta"
            on_release: app.root.current = "ventas"
        Btn:
            text: "💸 Registrar gasto"
            on_release: app.root.current = "gastos"
        Btn:
            text: "👥 Clientes"
            on_release: app.root.current = "clientes"
        Btn:
            text: "🔄 Actualizar resumen"
            on_release: root.actualizar()
        Btn:
            text: "🚪 Salir"
            on_release: app.stop()

<Ventas>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(15)
        spacing: dp(8)
        Title:
            text: "💰 Nueva venta"
        TextInputBox:
            id: producto
            hint_text: "Producto o servicio"
        TextInputBox:
            id: cantidad
            hint_text: "Cantidad"
            input_filter: "float"
        TextInputBox:
            id: precio
            hint_text: "Precio total"
            input_filter: "float"
        Label:
            id: mensaje
            text: ""
        Btn:
            text: "Guardar venta"
            on_release: root.guardar()
        Btn:
            text: "Volver"
            on_release: app.root.current = "inicio"

<Gastos>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(15)
        spacing: dp(8)
        Title:
            text: "💸 Nuevo gasto"
        TextInputBox:
            id: concepto
            hint_text: "Concepto del gasto"
        TextInputBox:
            id: monto
            hint_text: "Monto"
            input_filter: "float"
        Label:
            id: mensaje
            text: ""
        Btn:
            text: "Guardar gasto"
            on_release: root.guardar()
        Btn:
            text: "Volver"
            on_release: app.root.current = "inicio"

<Clientes>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(15)
        spacing: dp(8)
        Title:
            text: "👥 Clientes"
        TextInputBox:
            id: nombre
            hint_text: "Nombre del cliente"
        TextInputBox:
            id: telefono
            hint_text: "Teléfono"
        Label:
            id: mensaje
            text: ""
        Btn:
            text: "Guardar cliente"
            on_release: root.guardar()
        Btn:
            text: "Volver"
            on_release: app.root.current = "inicio"
"""

def conectar():
    return sqlite3.connect(DB)

def preparar_db():
    con = conectar()
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS ventas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto TEXT,
        cantidad REAL,
        total REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS gastos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        concepto TEXT,
        monto REAL
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS clientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        telefono TEXT
    )""")
    con.commit()
    con.close()

class Inicio(Screen):
    resumen = StringProperty("Cargando...")

    def on_pre_enter(self):
        self.actualizar()

    def actualizar(self):
        con = conectar()
        cur = con.cursor()
        cur.execute("SELECT COALESCE(SUM(total),0) FROM ventas")
        ventas = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(monto),0) FROM gastos")
        gastos = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM clientes")
        clientes = cur.fetchone()[0]
        con.close()
        saldo = ventas - gastos
        self.resumen = (
            f"Ventas: S/ {ventas:.2f}\n"
            f"Gastos: S/ {gastos:.2f}\n"
            f"Saldo: S/ {saldo:.2f}\n"
            f"Clientes: {clientes}"
        )

class Ventas(Screen):
    def guardar(self):
        try:
            producto = self.ids.producto.text.strip()
            cantidad = float(self.ids.cantidad.text)
            precio = float(self.ids.precio.text)
            if not producto or cantidad <= 0 or precio < 0:
                raise ValueError
            con = conectar()
            con.execute(
                "INSERT INTO ventas(producto,cantidad,total) VALUES(?,?,?)",
                (producto, cantidad, precio)
            )
            con.commit()
            con.close()
            self.ids.producto.text = ""
            self.ids.cantidad.text = ""
            self.ids.precio.text = ""
            self.ids.mensaje.text = "✅ Venta guardada"
        except ValueError:
            self.ids.mensaje.text = "⚠️ Completa los datos correctamente"

class Gastos(Screen):
    def guardar(self):
        try:
            concepto = self.ids.concepto.text.strip()
            monto = float(self.ids.monto.text)
            if not concepto or monto < 0:
                raise ValueError
            con = conectar()
            con.execute(
                "INSERT INTO gastos(concepto,monto) VALUES(?,?)",
                (concepto, monto)
            )
            con.commit()
            con.close()
            self.ids.concepto.text = ""
            self.ids.monto.text = ""
            self.ids.mensaje.text = "✅ Gasto guardado"
        except ValueError:
            self.ids.mensaje.text = "⚠️ Completa los datos correctamente"

class Clientes(Screen):
    def guardar(self):
        nombre = self.ids.nombre.text.strip()
        telefono = self.ids.telefono.text.strip()
        if not nombre:
            self.ids.mensaje.text = "⚠️ Escribe el nombre"
            return
        con = conectar()
        con.execute(
            "INSERT INTO clientes(nombre,telefono) VALUES(?,?)",
            (nombre, telefono)
        )
        con.commit()
        con.close()
        self.ids.nombre.text = ""
        self.ids.telefono.text = ""
        self.ids.mensaje.text = "✅ Cliente guardado"

class NegocioApp(App):
    def build(self):
        preparar_db()
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(Inicio(name="inicio"))
        sm.add_widget(Ventas(name="ventas"))
        sm.add_widget(Gastos(name="gastos"))
        sm.add_widget(Clientes(name="clientes"))
        return sm

if __name__ == "__main__":
    NegocioApp().run()
