import socket
import struct
import os
import random

IP = ""
PORTA = 8080
FORMATO_CABECALHO = "!IIB"          # seq_num (I) + trans_id (I) + flag (B) = 9 bytes
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)
FORMATO_ACK = "!I"                  # ACK = apenas o numero de sequencia confirmado
NOME_SAIDA = "recebido.pdf"

# Tarefa A: tempo maximo aguardando o proximo pacote antes de abortar
TIMEOUT_TRANSACAO = 10.0
# Tarefa B: simulador de rede ruim (descarta pacotes na chegada)
SIMULAR_REDE_RUIM = True
CHANCE_PERDA = 0.3

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))
sock.settimeout(TIMEOUT_TRANSACAO)   # Tarefa A: recvfrom estoura apos 10s
print(f"[*] Servidor UDP aguardando em {IP or '0.0.0.0'}:{PORTA}...")

seq_esperado = 0
arquivo_destino = open(NOME_SAIDA, "wb")
transacao_atual = None

try:
    while True:
        try:
            pacote, endereco_cliente = sock.recvfrom(2048)
        except socket.timeout:
            # Tarefa A (rollback): se a transferencia ja tinha comecado, o cliente
            # sumiu -> apaga o arquivo incompleto do disco.
            if transacao_atual is not None:
                print("[X] 10s sem pacotes. Cliente desistiu. Abortando transacao.")
                arquivo_destino.close()
                os.remove(NOME_SAIDA)
                print(f"[X] Arquivo incompleto '{NOME_SAIDA}' removido do disco.")
                break
            continue   # ainda nao chegou nenhum cliente: segue aguardando

        # Tarefa B: simula perda do pacote recebido
        if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:
            print("[SIMULACAO] Pacote perdido na rede...")
            continue

        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        if transacao_atual is None:
            transacao_atual = trans_id
        if trans_id != transacao_atual:
            continue   # ignora pacotes de outra transacao

        if seq_num == seq_esperado:
            arquivo_destino.write(payload)
            seq_esperado += 1
            sock.sendto(struct.pack(FORMATO_ACK, seq_num), endereco_cliente)
            if flag == 1:
                print("[*] Ultimo pacote recebido. Transferencia concluida.")
                break
        else:
            # pacote duplicado (ACK anterior se perdeu): reenvia o ultimo ACK valido
            sock.sendto(struct.pack(FORMATO_ACK, seq_esperado - 1), endereco_cliente)
finally:
    if not arquivo_destino.closed:
        arquivo_destino.close()
    sock.close()
