import socket
import threading
from tabulate import tabulate

# Implementacao de Clocks Logicos de Lamport com aplicacao servidor-cliente

class LamportClock:
    def __init__(self, node_id):
        self.clock = 0
        self.node_id = node_id

    def increment(self):
        self.clock += 1

    def send_event(self, receiver_id):
        self.increment()
        return self.clock, f"Mensagem enviada para {receiver_id}"

    def receive_event(self, received_clock, sender_id):
        self.clock = max(self.clock, received_clock) + 1
        return self.clock, f"Mensagem recebida de {sender_id}"

# Servidor para gerenciar comunicacao entre nos

def server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))
    server_socket.listen(3)
    print("Servidor iniciado. Aguardando conexoes...")

    clients = []
    event_log = []

    def handle_client(client_socket, addr):
        nonlocal event_log
        node_id = client_socket.recv(1024).decode()
        print(f"{node_id} conectado de {addr}")
        clock = LamportClock(node_id)

        while True:
            try:
                msg = client_socket.recv(1024).decode()
                if not msg:
                    break
                sender_clock = int(msg.split(',')[1])
                sender_id = msg.split(',')[0]
                updated_clock, desc = clock.receive_event(sender_clock, sender_id)
                event_log.append([node_id, 'Recepcao', updated_clock, desc])
                print(f"{desc} - Timestamp: {updated_clock}")
            except:
                break

        client_socket.close()
        print(f"Conexao encerrada com {node_id}")

        # Exibir tabela de eventos ao finalizar a conexao
        if len(event_log) > 0:
            print("\nLog de eventos:")
            headers = ["No", "Tipo de Evento", "Clock", "Descricao"]
            print(tabulate(event_log, headers=headers, tablefmt="grid"))

    while len(clients) < 3:
        client_socket, addr = server_socket.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, addr)).start()

# Cliente que representa um no

def client(node_id):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    client_socket.send(node_id.encode())
    clock = LamportClock(node_id)

    # Simulacao de eventos
    clock.increment()
    print(f"{node_id} executou evento local - Clock: {clock.clock}")

    for receiver in ['A', 'B', 'C']:
        if receiver != node_id:
            sent_clock, desc = clock.send_event(receiver)
            message = f"{node_id},{sent_clock}"
            client_socket.send(message.encode())
            print(f"{desc} - Timestamp: {sent_clock}")

    client_socket.close()

# Iniciando servidor e clientes em threads diferentes
if __name__ == "__main__":
    server_thread = threading.Thread(target=server)
    server_thread.start()

    client_threads = []
    for node in ['A', 'B', 'C']:
        t = threading.Thread(target=client, args=(node,))
        client_threads.append(t)
        t.start()

    for t in client_threads:
        t.join()

    server_thread.join()
