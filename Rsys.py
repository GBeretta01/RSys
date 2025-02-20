import streamlit as st
import sqlite3

# Conectar a la base de datos SQLite (o crearla si no existe)
conn = sqlite3.connect('inventario.db')
c = conn.cursor()

# Crear la tabla de productos si no existe
c.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    cantidad INTEGER NOT NULL,
    precio REAL NOT NULL
)
''')
conn.commit()

# Función para agregar un producto
def agregar_producto(nombre, cantidad, precio):
    c.execute('INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)', (nombre, cantidad, precio))
    conn.commit()

# Función para actualizar un producto
def actualizar_producto(id, cantidad):
    c.execute('UPDATE productos SET cantidad = ? WHERE id = ?', (cantidad, id))
    conn.commit()

# Función para eliminar un producto
def eliminar_producto(id):
    c.execute('DELETE FROM productos WHERE id = ?', (id,))
    conn.commit()

# Función para obtener todos los productos
def obtener_productos():
    c.execute('SELECT * FROM productos')
    return c.fetchall()

# Interfaz de Streamlit
st.title("Sistema de Inventario")

# Menú de opciones
opcion = st.sidebar.selectbox("Menú", ["Ver Inventario", "Agregar Producto", "Actualizar Producto", "Eliminar Producto"])

if opcion == "Ver Inventario":
    st.header("Inventario Actual")
    productos = obtener_productos()
    if productos:
        st.table(productos)
    else:
        st.warning("No hay productos en el inventario.")

elif opcion == "Agregar Producto":
    st.header("Agregar Nuevo Producto")
    nombre = st.text_input("Nombre del Producto")
    cantidad = st.number_input("Cantidad", min_value=0)
    precio = st.number_input("Precio", min_value=0.0)
    if st.button("Agregar"):
        agregar_producto(nombre, cantidad, precio)
        st.success("Producto agregado exitosamente.")

elif opcion == "Actualizar Producto":
    st.header("Actualizar Producto")
    productos = obtener_productos()
    if productos:
        producto_id = st.selectbox("Selecciona un producto", [p[0] for p in productos])
        nueva_cantidad = st.number_input("Nueva Cantidad", min_value=0)
        if st.button("Actualizar"):
            actualizar_producto(producto_id, nueva_cantidad)
            st.success("Producto actualizado exitosamente.")
    else:
        st.warning("No hay productos para actualizar.")

elif opcion == "Eliminar Producto":
    st.header("Eliminar Producto")
    productos = obtener_productos()
    if productos:
        producto_id = st.selectbox("Selecciona un producto", [p[0] for p in productos])
        if st.button("Eliminar"):
            eliminar_producto(producto_id)
            st.success("Producto eliminado exitosamente.")
    else:
        st.warning("No hay productos para eliminar.")

# Cerrar la conexión a la base de datos al finalizar
conn.close()