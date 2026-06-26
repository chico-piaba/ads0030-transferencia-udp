# =============================================================
#  SERVIDOR (RECEPTOR) - Protocolo SRTP sobre UDP
#  VERSAO DE ESTUDO (comentada). A versao de entrega esta em ../entrega/
#  Disciplina: ADS0030 - Programacao em Ambiente de Rede
# =============================================================

import socket
import struct
import os        # Tarefa A: usado em os.remove() para apagar arquivo incompleto
import random    # Tarefa B: usado para sortear quais pacotes "perder"

# --- Parametros da rede --------------------------------------
IP = ""                       # "" = escuta em todas as interfaces da maquina
PORTA = 8080

# --- Formato do cabecalho (Secao 6 do enunciado) -------------
# "!IIB" -> Network Byte Order (Big-Endian):
#   I = seq_num  (4 bytes) numero de sequencia do pacote
#   I = trans_id (4 bytes) id unico da transferencia
#   B = flag     (1 byte)  1 = ultimo pacote, 0 = ha mais dados
FORMATO_CABECALHO = "!IIB"
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)   # = 9

# ACK (Servidor -> Cliente): so o numero de sequencia confirmado
FORMATO_ACK = "!I"

NOME_SAIDA = "recebido.pdf"

# --- Tarefa A: controle de transacao / rollback --------------
TIMEOUT_TRANSACAO = 10.0      # se ficar 10s sem pacote, aborta e apaga o arquivo

# --- Tarefa B: simulador de rede ruim ------------------------
SIMULAR_REDE_RUIM = True      # descarta pacotes na CHEGADA (lado servidor)
CHANCE_PERDA = 0.3            # 30% de chance de "perder" cada pacote

# --- Socket UDP ----------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))
# Tarefa A: define o timeout do recvfrom. Se passar 10s sem receber nada,
# o recvfrom levanta socket.timeout (tratado no loop abaixo).
sock.settimeout(TIMEOUT_TRANSACAO)
print(f"[*] Servidor UDP aguardando em {IP or '0.0.0.0'}:{PORTA}...")

# --- Estado da transferencia ---------------------------------
seq_esperado = 0                              # proximo seq_num que esperamos gravar
arquivo_destino = open(NOME_SAIDA, "wb")      # arquivo de saida (vai sendo montado)
transacao_atual = None                        # trava na 1a transacao que aparecer

try:
    while True:
        # ---- Recebe um pacote (buffer > MTU) ----------------
        try:
            pacote, endereco_cliente = sock.recvfrom(2048)
        except socket.timeout:
            # ---- Tarefa A (ROLLBACK) ------------------------
            # Passaram-se 10s sem nenhum pacote. Se a transferencia ja
            # tinha comecado (transacao_atual != None), concluimos que o
            # cliente morreu/desistiu -> apagamos o arquivo pela metade.
            if transacao_atual is not None:
                print("[X] 10s sem pacotes. Cliente desistiu. Abortando transacao.")
                arquivo_destino.close()
                os.remove(NOME_SAIDA)              # apaga o arquivo corrompido/incompleto
                print(f"[X] Arquivo incompleto '{NOME_SAIDA}' removido do disco.")
                break
            # Ainda nao chegou nenhum cliente: continua aguardando.
            continue

        # ---- Tarefa B: simula perda do pacote recebido ------
        if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:
            print("[SIMULACAO] Pacote perdido na rede...")
            continue   # ignora: o cliente vai estourar o timeout e retransmitir

        # ---- Separa cabecalho e payload ---------------------
        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        # ---- Trava na primeira transacao --------------------
        if transacao_atual is None:
            transacao_atual = trans_id
            print(f"[*] Nova transferencia (ID {trans_id}).")
        if trans_id != transacao_atual:
            continue   # ignora pacotes de outra transferencia (alienigenas)

        # ---- Pacote na ordem certa: grava e confirma --------
        if seq_num == seq_esperado:
            arquivo_destino.write(payload)
            seq_esperado += 1
            sock.sendto(struct.pack(FORMATO_ACK, seq_num), endereco_cliente)
            if flag == 1:
                print("[*] Ultimo pacote recebido. Transferencia concluida.")
                break
        else:
            # ---- Pacote DUPLICADO -------------------------------
            # Acontece quando o ACK anterior se perdeu e o cliente
            # reenviou o mesmo pacote. Nao gravamos de novo; apenas
            # reenviamos o ACK do ultimo pacote que ja gravamos.
            sock.sendto(struct.pack(FORMATO_ACK, seq_esperado - 1), endereco_cliente)
finally:
    if not arquivo_destino.closed:
        arquivo_destino.close()
    sock.close()
