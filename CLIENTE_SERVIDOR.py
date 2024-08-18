import socket
import threading

class ClientServer:
    def __init__(self, host='localhost', server_port=12345):
        self.server_address = (host, server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

        self.client_name = input("Digite seu nome: ")
        self.client_socket.sendall(self.client_name.encode('utf-8'))

        # Solicita a porta ao usuário para evitar conflitos
        client_port = int(input("Digite a porta para o seu cliente: "))
        self.client_socket.sendall(str(client_port).encode('utf-8'))  # Envia a porta para o servidor

        self.messages = []
        self.all_chat = []

        # Cliente servidor para receber mensagens
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_socket.bind(('localhost', client_port))
        self.listen_socket.listen()

        threading.Thread(target=self.listen_for_messages).start()

    def listen_for_messages(self):
        while True:
            conn, _ = self.listen_socket.accept()
            message = conn.recv(1024).decode('utf-8')
            self.messages.append(message)
            self.all_chat.append(message)
            conn.close()

    def send_message(self, recipient_ip, recipient_port, message):
        recipient_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        recipient_socket.connect((recipient_ip, recipient_port))
        recipient_socket.sendall(f"{self.client_name}: {message}".encode('utf-8'))
        recipient_socket.close()

    def send_message_to_all(self, message):
        clients = self.list_connected_clients()
        for client in clients:
            recipient_ip_port = client.split(": ")[1]  # Formato é "nome: IP:PORTA"
            recipient_ip, recipient_port = recipient_ip_port.split(":")
            self.send_message(recipient_ip, int(recipient_port), message)

    def list_messages(self):
        if self.messages:
            print("Mensagens recebidas:")
            for msg in self.messages:
                print(msg)
        else:
            print("Nenhuma mensagem recebida.")

    def list_all_chat(self):
        if self.all_chat:
            print("Chat All:")
            for msg in self.all_chat:
                # Filtra mensagens para todos (sem destinatário específico)
                if "Para todos:" in msg:
                    print(msg)
        else:
            print("Nenhuma mensagem no chat all.")

    def list_connected_clients(self):
        self.client_socket.sendall("LIST".encode('utf-8'))
        clients_list = self.client_socket.recv(4096).decode('utf-8')
        clients = clients_list.splitlines()
        clients = [client for client in clients if not client.startswith(self.client_name)]
        return clients

    def select_recipient(self):
        clients = self.list_connected_clients()
        if not clients:
            print("Nenhum cliente conectado.")
            return None, None

        print("Clientes conectados:")
        for i, client in enumerate(clients):
            print(f"{i + 1}. {client}")

        try:
            choice = int(input("Escolha o número do destinatário: ")) - 1
            if 0 <= choice < len(clients):
                selected_client = clients[choice]
                recipient_ip_port = selected_client.split(": ")[1]  # Formato é "nome: IP:PORTA"
                recipient_ip, recipient_port = recipient_ip_port.split(":")
                return recipient_ip, int(recipient_port)
            else:
                print("Escolha inválida.")
                return None, None
        except (ValueError, IndexError):
            print("Escolha inválida.")
            return None, None

    def start(self):
        while True:
            print("\nMenu:")
            print("1. Enviar mensagem")
            print("2. Listar mensagens recebidas")
            print("3. Listar mensagens do chat all")
            print("4. Listar clientes conectados")
            print("5. Sair")
            option = input("Escolha uma opção: ")

            if option == '1':
                print("1. Enviar mensagem para um cliente")
                print("2. Enviar mensagem para todos os clientes")
                sub_option = input("Escolha uma opção: ")

                if sub_option == '1':
                    recipient_ip, recipient_port = self.select_recipient()
                    if recipient_ip and recipient_port:
                        message = input("Digite a mensagem: ")
                        self.send_message(recipient_ip, recipient_port, message)

                elif sub_option == '2':
                    message = input("Digite a mensagem para todos: ")
                    self.send_message_to_all(f"Para todos: {message}")

                else:
                    print("Opção inválida.")

            elif option == '2':
                self.list_messages()

            elif option == '3':
                self.list_all_chat()

            elif option == '4':
                clients = self.list_connected_clients()
                if clients:
                    print("Clientes conectados:")
                    for client in clients:
                        print(client)
                else:
                    print("Nenhum cliente conectado.")

            elif option == '5':
                self.client_socket.close()
                print("Conexão fechada.")
                break

            else:
                print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    client = ClientServer()
    client.start()
