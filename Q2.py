import threading
import random
import time
from queue import Queue

# Variáveis globais
estado_global = []
marcadores_enviados = set()
lock = threading.Lock()

# Fila de mensagens para cada processo
mensagens = {1: Queue(), 2: Queue(), 3: Queue()}

# Função para salvar o estado de um processo
def salvar_estado(process_id):
    estado = random.randint(1, 100)  # Simula um estado aleatório
    return f"Estado de P{process_id}: {estado}"

# Função para capturar o estado de todos os processos
def captura_estado(process_id, processos, iniciar=False):
    # Inicia a captura de estado se for o processo inicial
    if iniciar:
        print(f"Processo P{process_id} iniciou a captura de estado.")
        # Salva o estado local
        estado_local = salvar_estado(process_id)
        estado_global.append(estado_local)
        print(f"{estado_local} (salvo localmente)")

        # Envia marcador para os outros processos
        for pid in processos:
            if pid != process_id:
                enviar_marcador(process_id, pid)
    else:
        print(f"Processo P{process_id} recebeu marcador.")
        # Salva o estado local
        estado_local = salvar_estado(process_id)
        estado_global.append(estado_local)
        print(f"{estado_local} (salvo localmente)")

        # Envia marcador para os outros processos
        for pid in processos:
            if pid != process_id:
                enviar_marcador(process_id, pid)

    # Processa as mensagens na fila do processo
    while not mensagens[process_id].empty():
        msg = mensagens[process_id].get()
        print(f"Processo P{process_id} processando mensagem: {msg}")

# Função para enviar marcador a outro processo
def enviar_marcador(from_pid, to_pid):
    with lock:
        if (from_pid, to_pid) not in marcadores_enviados:
            print(f"Processo P{from_pid} enviando marcador para P{to_pid}.")
            marcadores_enviados.add((from_pid, to_pid))

            # Envia o marcador para o outro processo
            mensagens[to_pid].put(f"Marcador de P{from_pid} para P{to_pid}")
            # Chama a captura de estado do outro processo
            captura_estado(to_pid, processos=[1, 2, 3])

# Função para simular a rede distribuída
def rede_distribuida():
    processos = [1, 2, 3]
    # Processo 1 inicia a captura de estado
    captura_estado(1, processos, iniciar=True)
    # Espera algum tempo para simular comunicação entre processos
    time.sleep(2)

    # Agora, os processos que receberam mensagens devem processá-las
    for pid in processos:
        captura_estado(pid, processos)

    print("\nEstado Global Capturado:")
    for estado in estado_global:
        print(estado)

# Criação de threads para simular processos em paralelo
t1 = threading.Thread(target=rede_distribuida)
t1.start()
t1.join()
