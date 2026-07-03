import socket
import struct
import os
import random
import datetime

FORMATO_CABECALHO = "!IIB"          # seq_num (I) + trans_id (I) + flag (B) = 9 bytes
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)
FORMATO_ACK = "!I"                  # ACK = apenas o numero de sequencia confirmado
NOME_SAIDA = "recebido.jpg"
TIMEOUT_TRANSACAO = 10.             # Tarefa A: tempo maximo aguardando o proximo pacote antes de abortar
SIMULAR_REDE_RUIM = True            # Tarefa B: simulador de rede ruim (descarta pacotes na chegada)
CHANCE_PERDA = 0.3                  # grau de chances de formar a simulação de rede/conexão ruim
YELLOW = '\033[33m'                 # cor amarela no texto do terminal na cor amarelo



def log_cat(text):                  # função para log formatado
    timeStr = datetime.datetime.now().strftime("%H:%M %S")
    print(f"{YELLOW}{timeStr} -> {text}")
    

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # conecta com o servidor caso ele estena com a porta 8080 aberta
    sock.bind(("localhost", 8080))                          # vinculando-se a porta 8080
    sock.settimeout(TIMEOUT_TRANSACAO)                      # Tarefa A: definição do timeout de 10s para detectar ausencia do cliente
    log_cat(f"Servidor UDP aberto.")
    seq_esperado = 0
    arquivo_destino = open(NOME_SAIDA, "wb")                # cria e define que a escritura de arquivos será do tipo byte-array puro
    transacao_atual = None
    
    log_cat("--------------- Aguardando envio do arquivo ------------------")
    try:
        while True:
            try:
                pacote, endereco_cliente = sock.recvfrom(2048)                                      # recebendo dados oriundos do cliente
            except socket.timeout:
                
                if transacao_atual is not None:                                                     # Tarefa A (rollback): se a transferencia ja tinha comecado, o cliente
                    log_cat("10s sem pacotes. Cliente desistiu. Abortando transacao.")              # sumiu -> apaga o arquivo incompleto do disco.
                    arquivo_destino.close()
                    os.remove(NOME_SAIDA)
                    log_cat(f"Arquivo recebido e corrompido '{NOME_SAIDA}' removido do disco.")
                    break
                continue                                                                            # pula as linhas seguintes e volta para a primeira caso nao haja cliente vinculado

            
            if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:                                # Tarefa B: simula perda do pacote recebido
                log_cat("-[SIMULACAO] Pacote perdido na rede... Nao enviando reconhecimento(ACK).")
                continue                                                                            # Tarefa B: nao envia o reconhecimento(ACK) para o cliente para simular uma perda de dados

            cabecalho_bytes = pacote[:TAMANHO_CABECALHO]                                            # captura do cabeçalho (header) oriundos do cliente
            payload = pacote[TAMANHO_CABECALHO:]                                                    # captura do pacote de dados oriundos do cliente
            seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)             # descompactando os dados do cabeçalho

            if transacao_atual is None: transacao_atual = trans_id                                  
            if trans_id != transacao_atual: continue                                                # ignora pacotes de outra transacao
            log_cat(f"Pacote recebido. Numero do pacote: {seq_num}")

            if seq_num == seq_esperado:                                                             # verifica se a sequencia de pacotes está correta 
                arquivo_destino.write(payload)                                                      # escreve no arquivo aberto na linha 29
                seq_esperado += 1
                sock.sendto(struct.pack(FORMATO_ACK, seq_num), endereco_cliente)                    # enviando reconhecimento(ACK)
                if flag == 1:
                    log_cat("Ultimo pacote recebido. Transferencia concluida.")
                    break
            else:
                
                sock.sendto(struct.pack(FORMATO_ACK, seq_esperado - 1), endereco_cliente)           # pacote duplicado (ACK anterior se perdeu): reenvia o ultimo ACK valido
    finally:
        if not arquivo_destino.closed:
            arquivo_destino.close()                                                                 # fecha o filesystem (FS) do arquivo eberto na linha 29 para a manipulação do arquivo seja habilitada
        sock.close()                                                                                # fechamento da porta aberta na linha 52
    
try:                                                                                                # bloco "tentar" pois a função main irá quebrar ao tocar em CTRL + C
    main()                                                                                          # bloco "tentar" pois a função main irá quebrar ao tocar em CTRL + C
except KeyboardInterrupt:                                                                           # intercepta/detecta o CTRL + C
    log_cat("Servidor encerrado com (Ctrl+C)", cr=False)
