import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import hashlib  # Para encriptar contraseñas (opcional)

# Configuración inicial de la base de datos
def inicializar_db():
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    
    # Tabla de productos
    c.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL
    )''')
    
    # Tabla de facturas (existente)
    # ... (mantener igual que antes)
    
    # Nueva tabla de usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL CHECK(rol IN ('admin', 'usuario'))
    )''')
    
    # Nueva tabla de logs
    c.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        accion TEXT NOT NULL,
        fecha TEXT NOT NULL,
        detalle TEXT,
        FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
    )''')
    
    conn.commit()
    conn.close()

inicializar_db()

# =============================================
# Funciones de Autenticación y Roles
# =============================================
def autenticar_usuario(username, password):
    conn = sqlite3.connect('inantuario.db')
    c = conn.cursor()
    c.execute('SELECT id, username, password, rol FROM usuarios WHERE username = ?', (username,))
    usuario = c.fetchone()
    conn.close()
    
    if usuario:  # En producción, usar hashing!
        if usuario[2] == password:  # Esto es inseguro, solo para ejemplo
            return usuario
    return None

def registrar_log(usuario_id, accion, detalle=""):
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute('INSERT INTO logs (usuario_id, accion, fecha, detalle) VALUES (?, ?, ?, ?)',
              (usuario_id, accion, fecha, detalle))
    conn.commit()
    conn.close()

# =============================================
# Funciones de Gestión de Usuarios (Solo Admin)
# =============================================
def obtener_usuarios():
    conn = sqlite3.connect('inventario.db')
    df = pd.read_sql('SELECT id, username, rol FROM usuarios', conn)
    conn.close()
    return df

def crear_usuario(username, password, rol):
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)', 
                 (username, password, rol))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def eliminar_usuario(user_id, current_user_id):
    conn = sqlite3.connect('inventario.db')
    c = conn.cursor()
    
    if user_id == current_user_id:
        return "No puedes eliminarte a ti mismo"
    
    c.execute('SELECT COUNT(*) FROM usuarios WHERE rol = "admin"')
    num_admins = c.fetchone()[0]
    
    if num_admins <= 1:
        return "Debe haber al menos un administrador"
    
    c.execute('DELETE FROM usuarios WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return "Usuario eliminado"

# =============================================
# Interfaz de Streamlit
# =============================================
def main():
    st.title("Sistema de Inventario con Auditoría")
    
    # Inicializar sesión
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
        st.session_state.usuario = None
    
    # Login
    if not st.session_state.autenticado:
        st.subheader("Inicio de Sesión")
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar"):
            usuario = autenticar_usuario(username, password)
            if usuario:
                st.session_state.autenticado = True
                st.session_state.usuario = {
                    'id': usuario[0],
                    'username': usuario[1],
                    'rol': usuario[3]
                }
                registrar_log(usuario[0], "LOGIN", "Inicio de sesión exitoso")
                st.experimental_rerun()
            else:
                st.error("Credenciales incorrectas")
        return
    
    # Menú principal
    opciones = ["Inventario", "Facturas"]
    if st.session_state.usuario['rol'] == 'admin':
        opciones += ["Administración", "Registro de Actividad"]
    
    opcion = st.sidebar.selectbox("Menú", opciones)
    
    # Cerrar sesión
    if st.sidebar.button("Cerrar Sesión"):
        registrar_log(st.session_state.usuario['id'], "LOGOUT")
        st.session_state.autenticado = False
        st.experimental_rerun()
    
    # =============================================
    # Módulo de Inventario (Actualizado con Logs)
    # =============================================
    if opcion == "Inventario":
        st.header("Gestión de Inventario")
        
        # Funciones de productos
        conn = sqlite3.connect('inventario.db')
        
        # Agregar producto
        with st.expander("Agregar Nuevo Producto"):
            nombre = st.text_input("Nombre")
            cantidad = st.number_input("Cantidad", min_value=0)
            precio = st.number_input("Precio", min_value=0.0)
            if st.button("Guardar Producto"):
                c = conn.cursor()
                c.execute('INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)',
                         (nombre, cantidad, precio))
                conn.commit()
                producto_id = c.lastrowid
                registrar_log(st.session_state.usuario['id'], "ADD_PRODUCT", 
                              f"Producto ID: {producto_id} - {nombre}")
                st.success("Producto agregado")
        
        # Editar producto
        with st.expander("Editar Producto Existente"):
            productos = pd.read_sql('SELECT * FROM productos', conn)
            producto_id = st.selectbox("Seleccionar Producto", productos['id'])
            producto = productos[productos['id'] == producto_id].iloc[0]
            
            nuevo_nombre = st.text_input("Nombre", producto['nombre'])
            nueva_cantidad = st.number_input("Cantidad", value=producto['cantidad'])
            nuevo_precio = st.number_input("Precio", value=producto['precio'])
            
            if st.button("Actualizar Producto"):
                c = conn.cursor()
                c.execute('''
                    UPDATE productos 
                    SET nombre = ?, cantidad = ?, precio = ?
                    WHERE id = ?
                ''', (nuevo_nombre, nueva_cantidad, nuevo_precio, producto_id))
                conn.commit()
                registrar_log(st.session_state.usuario['id'], "EDIT_PRODUCT",
                             f"Producto ID: {producto_id} - Cambios: {nuevo_nombre}, {nueva_cantidad}, {nuevo_precio}")
                st.success("Producto actualizado")
        
        # Eliminar producto
        with st.expander("Eliminar Producto"):
            productos = pd.read_sql('SELECT * FROM productos', conn)
            producto_id = st.selectbox("Producto a Eliminar", productos['id'])
            if st.button("Confirmar Eliminación"):
                c = conn.cursor()
                producto_nombre = productos[productos['id'] == producto_id]['nombre'].values[0]
                c.execute('DELETE FROM productos WHERE id = ?', (producto_id,))
                conn.commit()
                registrar_log(st.session_state.usuario['id'], "DELETE_PRODUCT",
                             f"Producto ID: {producto_id} - {producto_nombre}")
                st.success("Producto eliminado")
        
        conn.close()
    
    # =============================================
    # Módulo de Administración (Solo Admin)
    # =============================================
    elif opcion == "Administración" and st.session_state.usuario['rol'] == 'admin':
        st.header("Administración del Sistema")
        
        # Gestión de usuarios
        st.subheader("Usuarios")
        usuarios = obtener_usuarios()
        st.table(usuarios)
        
        # Agregar usuario
        with st.expander("Nuevo Usuario"):
            nuevo_user = st.text_input("Nombre de usuario")
            nueva_pass = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["admin", "usuario"])
            if st.button("Crear Usuario"):
                if crear_usuario(nuevo_user, nueva_pass, rol):
                    registrar_log(st.session_state.usuario['id'], "ADD_USER",
                                 f"Usuario: {nuevo_user} - Rol: {rol}")
                    st.success("Usuario creado")
                else:
                    st.error("El usuario ya existe")
        
        # Eliminar usuario
        with st.expander("Eliminar Usuario"):
            usuario_id = st.selectbox("Usuario a Eliminar", usuarios['id'])
            if st.button("Confirmar Eliminación"):
                resultado = eliminar_usuario(usuario_id, st.session_state.usuario['id'])
                if "eliminado" in resultado:
                    registrar_log(st.session_state.usuario['id'], "DELETE_USER",
                                 f"Usuario ID: {usuario_id}")
                    st.success(resultado)
                else:
                    st.error(resultado)
    
    # =============================================
    # Módulo de Registro de Actividad
    # =============================================
    elif opcion == "Registro de Actividad" and st.session_state.usuario['rol'] == 'admin':
        st.header("Registro de Actividad")
        
        conn = sqlite3.connect('inventario.db')
        logs = pd.read_sql('''
            SELECT l.fecha, u.username, l.accion, l.detalle 
            FROM logs l
            JOIN usuarios u ON l.usuario_id = u.id
            ORDER BY l.fecha DESC
        ''', conn)
        conn.close()
        
        st.dataframe(logs)

# Ejecutar la aplicación
if __name__ == "__main__":
    main()