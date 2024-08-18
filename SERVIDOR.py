import socket
import threading

# Servidor central
class CentralServer:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.clients = {}  # Armazena clientes com nome, IP e porta

    def handle_client(self, client_socket, client_address):
        try:
            # Recebe o nome e a porta do cliente
            client_name = client_socket.recv(1024).decode('utf-8')
            client_port = client_socket.recv(1024).decode('utf-8')
            self.clients[client_name] = (client_address[0], client_port)
            print(f"{client_name} conectado de {client_address[0]}:{client_port}")

            while True:
                request = client_socket.recv(1024).decode('utf-8')
                if request == "LIST":
                    clients_list = "\n".join([f"{name}: {addr[0]}:{addr[1]}" for name, addr in self.clients.items()])
                    client_socket.sendall(clients_list.encode('utf-8'))

        except Exception as e:
            print(f"Erro ao conectar {client_address}: {e}")
        finally:
            if client_name in self.clients:
                del self.clients[client_name]
            client_socket.close()

    def start(self):
        print("Servidor central iniciado...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_handler.start()

if __name__ == "__main__":
    server = CentralServer()
    server.start()
