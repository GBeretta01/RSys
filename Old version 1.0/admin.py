import sqlite3
import user_admin
import inventory

conn = sqlite3.connect('ReginaDB.db')
cursor = conn.cursor()

def menu_admin():
    while True:
        print("---MENÚ ADMIN---")
        print("1. Gestionar usuarios")
        print("2. Inventario")
        print("3. Entradas")
        print("4. Salidas")
        print("x. Cerrar sesión")
        opc_ma = input("Ingrese una opción: ")

        if opc_ma == '1':
            user_admin.users()
        elif opc_ma == '2':
            inventory.menu_inventory()
        elif opc_ma == '3':
            break
        elif opc_ma == '4':
            break
        elif opc_ma == 'x':
            break
        else:
            print("Elija una opción correcta válida")