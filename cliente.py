import socket
import threading # hilos de procesos

print("""
      ##################################################################
        █▀ █▀█ █▀▀ █▄▀   █ ▀█▀   ▀█▀ █▀█   █▀▄▀█ █▀▀   █▀▀ █░█ ▄▀█ ▀█▀
        ▄█ █▄█ █▄▄ █░█   █ ░█░   ░█░ █▄█   █░▀░█ ██▄   █▄▄ █▀█ █▀█ ░█░
      ##################################################################
      """)

apodo = input("Ingrese su apodo: ")

# Conectamos al servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    cliente.connect(('127.0.0.1', 55555))
    print("Conectado al servidor")
    
# Si hubo un error de conexion
except ConnectionRefusedError:
    print("No se pudo conectar al servidor. Asegúrate de que el servidor este online")
    exit()


# Funcion recibir mensajes
def recibir():
    while True:
        # Intentamos recibir mensajes del servidor
        try:
            mensaje = cliente.recv(1024).decode('utf-8')
            if mensaje == 'NICK': # Si el servidor pide nuestro apodo
                cliente.send(apodo.encode('utf-8'))
            else:
                print(mensaje)
        # Si hubo un error al recibir mensajes cerramos
        except:
            print("Ocurrió un error!")
            cliente.close()
            break


# Funcion escribir mensajes
def escribir():
    while True:
        mensaje = f'{apodo}: {input("")}'
        cliente.send(mensaje.encode('utf-8'))


# Creamos los hilos correspondientes para las funciones recibir y escribir
hilo_recibir = threading.Thread(target=recibir)
hilo_recibir.start()

hilo_escribir = threading.Thread(target=escribir)
hilo_escribir.start()
