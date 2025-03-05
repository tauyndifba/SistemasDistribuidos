import threading
import random
import time
from queue import Queue

# Variáveis globais
estado_global = []
marcadores_enviados = set()
lock = threading.Lock()
processos_em_andamento = set()

# Fila de mensagens para cada processo
mensagens = {1: Queue(), 2: Queue(), 3: Queue()}

# Eventos para coordenar a sincronização
eventos = {1: threading.Event(), 2: threading.Event(), 3: threading.Event()}

# Função para salvar o estado de um processo
def salvar_estado(process_id):
    estado = random.randint(1, 100)  # Simula um estado aleatório
    return f"Estado de P{process_id}: {estado}"

# Função para capturar o estado de um processo
def captura_estado(process_id, processos, iniciar=False):
    with lock:
        if process_id in processos_em_andamento:
            return  # Se o processo já iniciou a captura, evita duplicação
        processos_em_andamento.add(process_id)

    print(f"Processo P{process_id} {'iniciou' if iniciar else 'recebeu'} a captura de estado.")
    
    # Salva o estado local
    estado_local = salvar_estado(process_id)
    estado_global.append(estado_local)
    print(f"{estado_local} (salvo localmente)")
    
    # Envia marcador para os outros processos
    for pid in processos:
        if pid != process_id:
            enviar_marcador(process_id, pid)
    
    # Sinaliza que o processo concluiu sua captura de estado
    eventos[process_id].set()

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
            mensagens[to_pid].put(f"Marcador de P{from_pid} para P{to_pid}")
            time.sleep(1)
            threading.Thread(target=captura_estado, args=(to_pid, [1, 2, 3])).start()

# Função para simular a rede distribuída
def rede_distribuida():
    processos = [1, 2, 3]
    captura_estado(1, processos, iniciar=True)
    
    # Espera a conclusão de todos os processos
    for pid in processos:
        eventos[pid].wait()
    
    print("\nEstado Global Capturado:")
    for estado in estado_global:
        print(estado)

# Criação de thread principal para simular os processos
t1 = threading.Thread(target=rede_distribuida)
t1.start()
t1.join()