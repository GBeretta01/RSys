# app.py
import streamlit as st
import pandas as pd
import time
import os
from datetime import datetime

# Configuración inicial de archivos CSV
USERS_FILE = 'users.csv'
PRODUCTS_FILE = 'productos.csv'

# Crear archivos CSV si no existen
def init_files():
    if not os.path.exists(USERS_FILE):
        df = pd.DataFrame(columns=['Id', 'user', 'password', 'role'])
        df.to_csv(USERS_FILE, index=False)
        
        # Crear usuario admin por defecto
        admin_data = pd.DataFrame([{'Id': 1, 'user': 'admin', 'password': 'admin', 'role': 'admin'}])
        admin_data.to_csv(USERS_FILE, mode='a', index=False, header=False)
    
    if not os.path.exists(PRODUCTS_FILE):
        df = pd.DataFrame(columns=[
            'Id', 'code', 'producto', 'inventario_inicial', 'entrada',
            'salida', 'existencia', 'existencia_minima', 'precio_compra',
            'precio_venta', 'fecha_actualizacion'
        ])
        df.to_csv(PRODUCTS_FILE, index=False)

init_files()

# Función de autenticación
def authenticate(username, password):
    users = pd.read_csv(USERS_FILE)
    user = users[(users['user'] == username) & (users['password'] == password)]
    return None if user.empty else user.iloc[0]

# Menú de administración de usuarios
def manage_users():
    st.header("Gestión de Usuarios")
    option = st.selectbox("Seleccione operación:", 
                        ["Ver usuarios", "Crear usuario", "Eliminar usuario", "Volver"])
    
    if option == "Ver usuarios":
        users = pd.read_csv(USERS_FILE)
        st.dataframe(users)
        
    elif option == "Crear usuario":
        with st.form("new_user"):
            new_user = st.text_input("Nombre de usuario")
            new_pass = st.text_input("Contraseña", type="password")
            role = st.selectbox("Rol", ["user", "admin"])
            
            if st.form_submit_button("Crear"):
                users = pd.read_csv(USERS_FILE)
                new_id = users['Id'].max() + 1 if not users.empty else 1
                new_data = pd.DataFrame([{
                    'Id': new_id,
                    'user': new_user,
                    'password': new_pass,
                    'role': role
                }])
                new_data.to_csv(USERS_FILE, mode='a', index=False, header=False)
                st.success("Usuario creado exitosamente!")
                
    elif option == "Eliminar usuario":
        users = pd.read_csv(USERS_FILE)
        if not users.empty:
            user_to_delete = st.selectbox("Seleccione usuario a eliminar", users['user'])
            if st.button("Eliminar"):
                updated_users = users[users['user'] != user_to_delete]
                updated_users.to_csv(USERS_FILE, index=False)
                st.success("Usuario eliminado exitosamente!")
        else:
            st.warning("No hay usuarios para eliminar")

# Gestión de inventario
def manage_inventory():
    st.header("Gestión de Inventario")
    option = st.selectbox("Seleccione operación:", 
                        ["Ver inventario", "Buscar producto", "Agregar producto", "Eliminar producto", "Volver"])
    
    if option == "Ver inventario":
        products = pd.read_csv(PRODUCTS_FILE)
        st.dataframe(products)
        
    elif option == "Buscar producto":
        search_term = st.text_input("Ingrese código o nombre del producto")
        if search_term:
            products = pd.read_csv(PRODUCTS_FILE)
            results = products[
                (products['code'].astype(str).str.contains(search_term)) |
                (products['producto'].str.contains(search_term, case=False))
            ]
            st.dataframe(results)
            
    elif option == "Agregar producto":
        with st.form("new_product"):
            code = st.text_input("Código del producto")
            name = st.text_input("Nombre del producto")
            quantity = st.number_input("Cantidad inicial", min_value=0)
            min_stock = st.number_input("Existencia mínima", min_value=0)
            buy_price = st.number_input("Precio de compra", min_value=0.0)
            sell_price = st.number_input("Precio de venta", min_value=0.0)
            
            if st.form_submit_button("Agregar"):
                products = pd.read_csv(PRODUCTS_FILE)
                new_id = products['Id'].max() + 1 if not products.empty else 1
                new_product = pd.DataFrame([{
                    'Id': new_id,
                    'code': code,
                    'producto': name,
                    'inventario_inicial': quantity,
                    'entrada': 0,
                    'salida': 0,
                    'existencia': quantity,
                    'existencia_minima': min_stock,
                    'precio_compra': buy_price,
                    'precio_venta': sell_price,
                    'fecha_actualizacion': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }])
                new_product.to_csv(PRODUCTS_FILE, mode='a', index=False, header=False)
                st.success("Producto agregado exitosamente!")
                
    elif option == "Eliminar producto":
        products = pd.read_csv(PRODUCTS_FILE)
        if not products.empty:
            product_to_delete = st.selectbox("Seleccione producto a eliminar", products['producto'])
            if st.button("Eliminar"):
                updated_products = products[products['producto'] != product_to_delete]
                updated_products.to_csv(PRODUCTS_FILE, index=False)
                st.success("Producto eliminado exitosamente!")
        else:
            st.warning("No hay productos para eliminar")

# Interfaz principal
def main():
    st.title("Sistema de Gestión Regina")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user = None
    
    if not st.session_state.logged_in:
        with st.form("login"):
            username = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")
            
            if st.form_submit_button("Iniciar sesión"):
                user = authenticate(username, password)
                if user is not None:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.success("Inicio de sesión exitoso!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")
    else:
        st.sidebar.header(f"Bienvenido, {st.session_state.user['user']}")
        if st.session_state.user['role'] == 'admin':
            menu_option = st.sidebar.selectbox("Menú Principal", 
                                              ["Usuarios", "Inventario", "Cerrar sesión"])
            
            if menu_option == "Usuarios":
                manage_users()
            elif menu_option == "Inventario":
                manage_inventory()
            elif menu_option == "Cerrar sesión":
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()
        else:
            # Menú para usuarios normales (puedes personalizar según necesidades)
            manage_inventory()
            if st.sidebar.button("Cerrar sesión"):
                st.session_state.logged_in = False
                st.session_state.user = None
                st.rerun()

if __name__ == "__main__":
    main()