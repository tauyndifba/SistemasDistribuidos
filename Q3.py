import threading
import time
import random

# Classe que representa um processo no algoritmo Bully
class Processo:
    def __init__(self, id, processos):
        self.id = id  # ID unico
        self.processos = processos  # Lista de outros processos
        self.ativo = True  # Status do processo
        self.coordenador = None  # ID do coordenador atual

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

# Funcao para simular o ambiente distribuido
def simular_bully():
    # Criando processos
    processos = [Processo(i, []) for i in range(1, 6)]
    
    # Atualizando a lista de processos de cada no
    for processo in processos:
        processo.processos = [p for p in processos if p.id != processo.id]
    
    # Definindo o processo inicial com maior ID como coordenador
    coordenador_inicial = max(processos, key=lambda p: p.id)
    for processo in processos:
        processo.coordenador = coordenador_inicial.id
    print(f"[INICIALIZACAO] Processo {coordenador_inicial.id} e o coordenador inicial.")

    # Simulando falha do coordenador
    time.sleep(2)
    coordenador_inicial.falhar()

    # Processo com ID 2 detecta a falha e inicia uma eleicao
    time.sleep(2)
    processos[1].iniciar_eleicao()

    # Recuperacao do antigo coordenador
    time.sleep(3)
    coordenador_inicial.recuperar()

# Iniciando a simulacao em uma thread
if __name__ == "__main__":
    thread = threading.Thread(target=simular_bully)
    thread.start()
    thread.join()
