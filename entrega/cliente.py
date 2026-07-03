import socket
import struct
import os
import random
import time
import datetime

IP_DESTINO = "127.0.0.1"
PORTA_DESTINO = 8080
NOME_ARQUIVO = "foto.jpg"           # coloque uma imagem/PDF real nesta pasta
TAMANHO_PAYLOAD = 1024
FORMATO_CABECALHO = "!IIB"          # seq_num (I) + trans_id (I) + flag (B) = 9 bytes
FORMATO_ACK = "!I"                  # mesmo formato de ACK do servidor
TAMANHO_ACK = struct.calcsize(FORMATO_ACK)
MAX_TENTATIVAS = 10                 # tentativas de envio em caso de não recebimendo de reconhecimento(ACK)
SIMULAR_REDE_RUIM = True            # Tarefa B: simulador de rede ruim (descarta ACKs na recepcao do cliente)
CHANCE_PERDA = 0.3                  # timeout do Stop-and-Wait
GREEN = '\033[32m'                  # apenas para formatacao de texto na cor verde
BLUE = '\033[34m'                   # apenas para formatacao de texto na cor azul



def log_cat(text, cr: bool | None = True):                  # função auxiliar para log formatado incluindo a (hora:minuto segundo)
    timeStr = datetime.datetime.now().strftime("%H:%M %S")
    if cr: print("\033[A\r\033[K", end="")                  # move o cursor para o inicio da linha e empurra a cor azul e imprime o texto
    print(f"{BLUE}{timeStr} -> {text}")
    
    

def log_progress(value, total, prefix = 'Progresso:'):      # função auxiliar para barra de progresso
    percentage = 100 * (value / float(total))
    percent = ("{0:." + str(1) + "f}").format(percentage)
    max_progress = 60                                       # definindo o cumprimento do trilho da barra de progresso com 60 caracteres
    progress = int(percentage / (100 / max_progress))       # calculo do progresso com base 60
    track = max_progress - progress
    bar = '█' * progress + '-' * track                      # █ caractere ASCII estendido. &#9608; em decimal
    log_cat(f'{GREEN}{prefix} |{bar}| {percent}%', cr=False)
    if value == total: print()
    
    

def main():                                                                         # função principal de execução
    trans_id = random.randint(1000, 9999)                                           # gera um numero aleatorio entre 1000 inclusive e 9999
    seq_num = 0
    tamanho_arquivo = os.path.getsize(NOME_ARQUIVO)
    inicio = time.perf_counter()                                                    # Questao 10.1: cronometro da transferencia
    numero_pacotes = int(tamanho_arquivo / TAMANHO_PAYLOAD) + (1 if tamanho_arquivo % TAMANHO_PAYLOAD == 0 else 0)
    falha_severa = False
    
    log_cat("--------------- Iniciando envio do arquivo ------------------")
    log_cat(f"Numero da transacao: {trans_id}", cr=False)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)                         # abertura da porta PORTA_DESTINO = 8080 (linha 9)
    sock.settimeout(1.0)                                                            #  definição do timeout de 1 segundo para reconhecimento(ACK)
    with open(NOME_ARQUIVO, "rb") as arquivo:
        while True:
            pedaco = arquivo.read(TAMANHO_PAYLOAD)                                  # pacote de bytes do arquivo de tamanho TAMANHO_PAYLOAD = 1024 (linha 11)
            flag = 1 if len(pedaco) < TAMANHO_PAYLOAD else 0
            pacote = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag) + pedaco
            ack_recebido = False
            tentativas = 0
            
            while not ack_recebido and tentativas < MAX_TENTATIVAS:
                try:
                    log_cat(f"Enviando pacote {seq_num}/{numero_pacotes}. Tentativa nº{tentativas + 1}. Aguardando reconhecimento(ACK)...")
                    log_progress(seq_num, numero_pacotes)                           # mostra a barra de progresso de forma automatica
                    sock.sendto(pacote, (IP_DESTINO, PORTA_DESTINO))                # envio do pacote
                    dados_ack, _ = sock.recvfrom(TAMANHO_ACK)                       # função que ler o reconhedimento(ACK) de pacote recebido
                    
                    if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:        # Tarefa B: simula perda do ACK -> reusa o caminho de timeout
                        log_cat("-[SIMULACAO] Forcando timeout.")
                        log_progress(seq_num, numero_pacotes)
                        time.sleep(1)                                               # delay adicionado apenas para facilitar a visualização do log no terminal
                        raise socket.timeout                                        # provocando excepção de timeout

                    ack_num = struct.unpack(FORMATO_ACK, dados_ack)[0]              # descompactando o pacote para se obter o cabeçalho e o pacote (header, payload)
                    if ack_num == seq_num:
                        ack_recebido = True
                        log_cat(f"Pacote recebido pelo servidor.")
                        if seq_num == numero_pacotes: break;                        # verifica se todos os pacotes foram enviados
                        log_progress(seq_num, numero_pacotes)
                except socket.timeout:
                    tentativas += 1
                    log_cat(f"-[SIMULACAO] Timeout ocorrido. Reconhecimendo(ACK) do ultimo pacote enviado, nao recebido.") # apenas para mostrar quando tiver simulando
                    log_progress(seq_num, numero_pacotes)
                time.sleep(1)                                                       # delay adicionado apenas para facilitar a visualização do log no terminal

            if not ack_recebido:
                falha_severa = True
                log_cat(f"Falha Severa: pacote {seq_num}/{numero_pacotes} sem reconhecimento(ACK) em {MAX_TENTATIVAS} tentativas de envio. Abortando envio.")
                break

            seq_num += 1
            if flag == 1:                                                               # verifica se o cliente ainda possui pacotes para ser enviado
                log_cat("Transferencia concluida com sucesso!", cr=False)
                print()
                break

    if not falha_severa:
        fim = time.perf_counter()                                                       # captura o tempo em segundos em formato float/double
        decorrido = fim - inicio                                                        # apenas para fins estatisticos
        kbps = (tamanho_arquivo / decorrido) / 1024                                     # apenas para fins estatisticos
        log_cat(f"{tamanho_arquivo} bytes em {decorrido:.3f}s  ->  {kbps:.3f} Kbps")    # apenas para fins estatisticos
    sock.close()                                                                        # fechamento da porta aberta na linha 52
    
try:                                                                                    # bloco "tentar" pois a função main irá quebrar ao tocar em CTRL + C
    main()
except KeyboardInterrupt:                                                               # intercepta/detecta o CTRL + C
    log_cat("-------------- Cliente encerrado com (Ctrl+C) -----------------")
