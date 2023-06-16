import time
import sqlite3
conn = sqlite3.connect('ReginaDB.db')
cursor = conn.cursor()

def menu_inventory():

    while True:
        
        print("///INVENTARIO///")
        print("1. Ver Inventario")
        print("2. Buscar")
        print("3. Filtrar")
        print("4. Agregar producto")
        print("5. Borrar producto")
        print("x. Volver")
        opc = input("Ingrese una opción: ")

        if opc == '1':
            show_inventory()
        elif opc == '2':
            show_inventory()
            search_inventory()
        elif opc == '3':
            filter_product()
        elif opc == '4':
            new_product()
        elif opc == '5':
            show_inventory()
            delete_product()
        else:
            print("Ingrese una opción válida")

def show_inventory():
    
    print("\t///PRODUCTOS///\n")
    cursor.execute('SELECT * FROM productos')
    result_inventory = cursor.fetchall()
    for row in result_inventory:
        print(row)

def search_inventory():
    code_s = input("Escanee|escriba el código del producto: ")
    conn.execute(f"SELECT Id, code, producto, entrada, salida, existencia, precio_venta FROM productos WHERE code == '{code_s}'")
    result_inventory = cursor.fetchall()

    if result_inventory:
        for row in result_inventory:
            print(row)
    else:
        print("No se pudo encontrar el producto.")

def new_product():

    code_s = input("Código del producto: ")
    producto_s = input("Nombre del producto: ")
    f_inventory = int(input("Cantidad ingresada: "))
    entry = 0
    output = 0
    e_inventory = f_inventory
    e_minimun_inventory = float(input("Ingrese la cantidad mínima de existencia [Si no hay escriba 0]: "))
    p_compra = float(input("Precio de compra: "))
    p_venta = float(input("Precio a la venta: "))

    conn.execute('INSERT INTO productos (code, producto, inventario_inicial, entrada, salida, existencia, existencia_minima, precio_compra, precio_venta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (code_s, producto_s, f_inventory, entry, output, e_inventory, e_minimun_inventory, p_compra, p_venta))
    conn.commit()
    print("Guardando producto...")
    time.sleep(1)

def delete_product():

    id_delete = input("Ingrese la ID del producto: ")
    cursor.execute(f'DELETE FROM productos WHERE Id == {id_delete}')
    cursor.execute('CREATE TABLE productos_temp AS SELECT code, producto, inventario_inicial, entrada, salida, existencia, existencia_minima, precio_compra, precio_venta FROM productos')
    cursor.execute('DROP TABLE productos')
    cursor.execute('CREATE TABLE productos (Id INTEGER PRIMARY KEY, code TEXT, producto TEXT, inventario_inicial INTEGER, entrada INTEGER, salida INTEGER, existencia INTEGER, existencia_minima INTEGER, precio_compra REAL, precio_venta REAL)')
    cursor.execute('INSERT INTO productos (code, producto, inventario_inicial, entrada, salida, existencia, existencia_minima, precio_compra, precio_venta) SELECT code, producto, inventario_inicial, entrada, salida, existencia, existencia_minima, precio_compra, precio_venta FROM productos_temp')
    cursor.execute('DROP TABLE productos_temp')
    conn.commit()
    print("Borrando producto...")
    time.sleep(1)

def filter_product():

    print("\t---FILTRAR PRODUCTO---\n")
    name_product = input("Nombre del producto: ")
    cursor.execute(f"SELECT * FROM productos WHERE producto LIKE '%{name_product}%'")
    result = cursor.fetchall()

    if len(result) > 0:
        print("Resultados de la búsqueda:")
        for row in result:
            print(f"ID: {row[0]}, Producto: {row[1]}, Precio: {row[9]}")
    else:
        print("No se encontraron productos que coincidan con la búsqueda.")