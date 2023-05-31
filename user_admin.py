import sqlite3
import time
conn = sqlite3.connect('ReginaDB.db')
cursor = conn.cursor()


def users():
    while True:
        print("---USUARIOS---")
        print("1. Ver usuarios")
        print("2. Crear usuario")
        print("3. Borrar usuario")
        print("x. Volver")
        opc_ma = input("Ingrese una opción: ")

        if opc_ma == '1':
            print("\t///USUARIOS///\n")
            show_users()
            input("ENTER para continuar... ") 
        elif opc_ma == '2':
            print("\t///NUEVO USUARIO///\n")
            new_user()
        elif opc_ma == '3':
            print("\t///BORRAR USUARIO///\n")
            show_users()
            delete_user()
        elif opc_ma == 'x':
            break
        else:
            print("Elija una opción correcta válida")

def show_users():
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()
    for row in result:
        print(row)   


def new_user():

    n_user = input("Nuevo user: ")
    n_pass = input("Contraseña: ")

    cursor.execute('INSERT INTO users (user, password) VALUES (?, ?)', (n_user, n_pass))
    conn.commit()
    print("Usuario guardado...")
    time.sleep(1)
    

def delete_user():
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()

    print("x. Volver")
    opc = input("Elija un ID a borrar: ")
    if opc == 'x':
        return
    try:
        chosen_index = int(opc)
        

        if chosen_index <= 1 or chosen_index >= len(result) + 1:
            print("Elija una opción válida... ")
        else:
            cursor.execute(f'DELETE FROM users WHERE id = {chosen_index}')
            cursor.execute('CREATE TABLE users_temp AS SELECT user, password FROM users')
            cursor.execute('DROP TABLE users')
            cursor.execute('CREATE TABLE users (Id INTEGER PRIMARY KEY, user TEXT, password TEXT)')
            cursor.execute('INSERT INTO users (user, password) SELECT user, password FROM users_temp')
            cursor.execute('DROP TABLE users_temp')
            conn.commit()
            print("Borrando usuario...")
            time.sleep(1)

    except ValueError:
        print("Ingrese una opción válida o x para volver...")
