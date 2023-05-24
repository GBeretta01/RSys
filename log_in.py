import sqlite3
import time
import colorama
conn = sqlite3.connect('ReginaDB.db')
cursor = conn.cursor()

def dots():
    for i in range(4):
        print("Iniciando sesión", end="")
        for j in range(i):
            print(".", end="")
        print()
        time.sleep(1)

def log_in():
    user_v = input("User: ")
    pass_v = input("Password: ")

    cursor.execute('SELECT * FROM users WHERE user = ? AND password = ?', (user_v, pass_v))
    log_in = cursor.fetchone()

    if log_in is not None and log_in[2] == pass_v:
        dots()
        return True
    else:
        print("User or pass no valid.")
        return False