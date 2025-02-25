import threading
import time
import random

# Classe que representa um processo no algoritmo Bully com Heartbeat
class Processo:
    def __init__(self, id, processos, monitor):
        self.id = id  # ID unico
        self.processos = processos  # Lista de outros processos
        self.monitor = monitor  # Monitor central
        self.ativo = True  # Status do processo
        self.coordenador = None  # ID do coordenador atual
        self.heartbeat_thread = threading.Thread(target=self.enviar_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()

    def enviar_heartbeat(self):
        while True:
            if self.ativo:
                self.monitor.receber_heartbeat(self.id)
            time.sleep(1)  # Intervalo de heartbeat

    def iniciar_eleicao(self):
        if not self.ativo:
            return

        print(f"[ELEICAO] Processo {self.id} detectou falha e iniciou uma eleicao!")
        maior_id = self.id
        
        # Envia mensagem de eleicao para processos com ID maior
        for processo in self.processos:
            if processo.id > self.id and processo.ativo:
                print(f"[MENSAGEM] Processo {self.id} envia mensagem de eleicao para Processo {processo.id}")
                resposta = processo.receber_mensagem_eleicao()
                if resposta:
                    maior_id = processo.id
        
        # Atualiza o coordenador
        self.coordenador = maior_id
        print(f"[COORDENADOR] Processo {self.id} reconhece o Processo {maior_id} como novo coordenador.")
        
        # Notifica todos os processos ativos
        for processo in self.processos:
            if processo.ativo:
                processo.atualizar_coordenador(maior_id)

    def receber_mensagem_eleicao(self):
        if self.ativo:
            print(f"[RESPOSTA] Processo {self.id} recebeu mensagem de eleicao e respondera.")
            return True
        return False

    def atualizar_coordenador(self, novo_coordenador):
        self.coordenador = novo_coordenador
        print(f"[ATUALIZACAO] Processo {self.id} atualizou seu coordenador para o Processo {novo_coordenador}.")

    def falhar(self):
        self.ativo = False
        print(f"[FALHA] Processo {self.id} falhou!")

    def recuperar(self):
        self.ativo = True
        print(f"[RECUPERACAO] Processo {self.id} se recuperou e iniciou uma eleicao!")
        self.iniciar_eleicao()

# Classe que representa o monitor central para detectar falhas
class Monitor:
    def __init__(self, timeout=3):
        self.heartbeats = {}
        self.timeout = timeout  # Tempo limite para detectar falha
        self.monitor_thread = threading.Thread(target=self.verificar_heartbeats)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        self.processos = []

    def registrar_processo(self, processo):
        self.processos.append(processo)
        self.heartbeats[processo.id] = time.time()

    def receber_heartbeat(self, processo_id):
        self.heartbeats[processo_id] = time.time()

    def verificar_heartbeats(self):
        while True:
            time.sleep(2)
            tempo_atual = time.time()
            for processo_id, ultimo_heartbeat in list(self.heartbeats.items()):
                if tempo_atual - ultimo_heartbeat > self.timeout:
                    print(f"[MONITOR] Falha detectada no Processo {processo_id}!")
                    for processo in self.processos:
                        if processo.id != processo_id and processo.ativo:
                            processo.iniciar_eleicao()
                            break

# Funcao para simular o ambiente distribuido com heartbeat
def simular_bully_com_heartbeat():
    monitor = Monitor()
    processos = [Processo(i, [], monitor) for i in range(1, 6)]
    
    for processo in processos:
        processo.processos = [p for p in processos if p.id != processo.id]
        monitor.registrar_processo(processo)
    
    coordenador_inicial = max(processos, key=lambda p: p.id)
    for processo in processos:
        processo.coordenador = coordenador_inicial.id
    print(f"[INICIALIZACAO] Processo {coordenador_inicial.id} e o coordenador inicial.")

    # Simulando falha do coordenador
    time.sleep(5)
    coordenador_inicial.falhar()

    # Recuperacao do antigo coordenador
    time.sleep(10)
    coordenador_inicial.recuperar()

# Iniciando a simulacao em uma thread
if __name__ == "__main__":
    thread = threading.Thread(target=simular_bully_com_heartbeat)
    thread.start()
    thread.join()
