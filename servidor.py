import socket
import select
import time

# Configuramos las direcciones
HOST = '127.0.0.1'  # localhost
PORT = 55555 

# Definimos el tipo de conexion y el protocolo
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Configuramos el host y port para que sean reutilizables
servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Le pasamos las configuraciones el server e iniciamos
servidor.bind((HOST, PORT))
servidor.listen(100)

# Creamos las listas de clientes/apodos
clientes = [servidor]
apodos = {}


# Creamos la funcion que elimina y desconecta a los clientes
def eliminar(cliente):
    if cliente in clientes:
        clientes.remove(cliente)
    if cliente in apodos:
        print(f"Cliente {apodos[cliente]} se ha desconectado")
        del apodos[cliente]
    cliente.close()


# Transmitimos los mensajes a todos (vocero)
def transmitir(mensaje, remitente=None):
    # Lista de clientes problematicos
    clientes_a_eliminar = []
    
    for cliente in clientes:
        if cliente != remitente and cliente != servidor:
            
            # Intentamos transmitir un mensaje
            for intento in range (3):
                try:
                    cliente.send(mensaje)
                    break
                
                except socket.error as error:
                    print(f"Error al enviar mensaje a un cliente: {error}\n        Reintentando: {intento+1}...")
                    time.sleep(1) # Esperamos antes de reintentar
            
            # Si luego de los 3 intentos no se puede
            else:
                clientes_a_eliminar.append(cliente)
    
    # Eliminamos a los clientes problematicos
    for cliente in clientes_a_eliminar:
        eliminar(cliente)
        transmitir(f"{apodos.get(cliente, 'Desconocido')} salió de la conversación.".encode('utf-8'))


# Manejamos la recepcion y transmision de mensajes de un cliente
def manejar(cliente):
    for intento in range(3):
        
        # Intentamos recibir un mensaje
        try:
            mensaje = cliente.recv(1024)
            if mensaje:
                transmitir(mensaje,cliente)
                return True
            
            else:
                # El cliente salio de forma limpia
                return False
            
        except socket.error as error:
            print(f"Error al recibir datos de un cliente: {error}\n        Reintentando: {intento+1}...")
            time.sleep(1)
            
    return False


# Aceptamos nuevas conexiones
def aceptar(servidor):
    cliente, direccion = servidor.accept()
    print(f"Se conectó la dirección {str(direccion)}")

    # Pedimos el apodo al cliente
    cliente.send('NICK'.encode('utf-8'))
    apodo = cliente.recv(1024).decode('utf-8')
    apodos[cliente] = apodo
    clientes.append(cliente)

    # Avisamos de la nueva conexión
    print(f"El apodo del cliente es '{apodo}'")
    transmitir(f"{apodo} se conectó a la conversación".encode('utf-8'), cliente)


print("""
      #######################################################################
      #                        SERVIDOR ONLINE                              #
      #######################################################################
      """)

print(f"-> Servidor escuchando en {HOST}:{PORT}")


while True:
    
    # Utilizamos select para monitorear sockets
    lectura, escritura, excepciones = select.select(clientes, [], clientes) # lectura, escritura, excepciones (error)

    # Por cada socket para leer
    for sock in lectura:

        if sock == servidor:
            aceptar(servidor)
        
        else:
            # Tratamos de recibir/transmitir
            if not manejar(sock):
                eliminar(sock)
    
    
    # Por cada socket con errores
    for sock in excepciones:
        eliminar(sock)
