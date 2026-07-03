# =============================================================
#  CLIENTE (EMISSOR) - Protocolo SRTP sobre UDP
#  VERSAO DE ESTUDO (comentada). A versao de entrega esta em ../entrega/
#  Disciplina: ADS0030 - Programacao em Ambiente de Rede
# =============================================================

import socket
import struct
import os        # Questao 10.1: os.path.getsize() para medir a vazao
import random
import time      # Questao 10.1: time.perf_counter() para cronometrar

# --- Parametros ----------------------------------------------
IP_DESTINO = "127.0.0.1"      # IP do servidor (localhost para teste local)
PORTA_DESTINO = 8080
NOME_ARQUIVO = "foto.jpg"     # coloque uma imagem/PDF real nesta pasta

TAMANHO_PAYLOAD = 1024        # bytes de arquivo por pacote (cabe no MTU; ver Pesquisa 4.1)
FORMATO_CABECALHO = "!IIB"    # igual ao servidor
FORMATO_ACK = "!I"            # igual ao servidor
TAMANHO_ACK = struct.calcsize(FORMATO_ACK)

# Comecamos com 5 (codigo base) e subimos para 15: com 30% de perda nos
# DOIS sentidos (dados + ACK), cada tentativa tem ~49% de sucesso, entao
# poucas tentativas as vezes nao bastam para um arquivo com muitos pacotes.
MAX_TENTATIVAS = 15

# --- Tarefa B: simulador de rede ruim (lado cliente) ---------
SIMULAR_REDE_RUIM = True      # descarta ACKs na RECEPCAO (lado cliente)
CHANCE_PERDA = 0.3

# --- Socket UDP ----------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Timeout do Stop-and-Wait: se o ACK nao chegar em 1s, retransmite.
sock.settimeout(1.0)

trans_id = random.randint(1000, 9999)   # identifica esta transferencia inteira
seq_num = 0
print(f"[*] Enviando {NOME_ARQUIVO} (transacao {trans_id})")

# ---- Questao 10.1: inicia o cronometro ----------------------
tamanho_arquivo = os.path.getsize(NOME_ARQUIVO)
inicio = time.perf_counter()

with open(NOME_ARQUIVO, "rb") as arquivo:
    while True:
        # ---- Le um pedaco do arquivo ------------------------
        pedaco = arquivo.read(TAMANHO_PAYLOAD)
        # Se leu menos que o tamanho cheio (ou nada), e o ultimo pacote.
        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD else 0

        # ---- Monta o pacote (cabecalho + payload) -----------
        pacote = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag) + pedaco

        # ---- Loop do Stop-and-Wait (envio + retransmissao) --
        ack_recebido = False
        tentativas = 0
        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                sock.sendto(pacote, (IP_DESTINO, PORTA_DESTINO))
                print(f"[>] Pacote {seq_num} enviado (tentativa {tentativas+1}). Aguardando ACK...")
                dados_ack, _ = sock.recvfrom(TAMANHO_ACK)

                # ---- Tarefa B: simula perda do ACK --------------
                # Recebemos o ACK, mas fingimos que ele se perdeu na rede.
                # Reaproveitamos o caminho do timeout levantando a excecao,
                # o que forca a retransmissao (mostra "Timeout" na tela).
                if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:
                    print("[SIMULACAO] ACK perdido na rede...")
                    raise socket.timeout

                # ---- ACK valido? --------------------------------
                ack_num = struct.unpack(FORMATO_ACK, dados_ack)[0]
                if ack_num == seq_num:
                    ack_recebido = True
                    print(f"[<] ACK {ack_num} recebido.")
            except socket.timeout:
                # Nao chegou ACK a tempo -> conta tentativa e retransmite.
                tentativas += 1
                print(f"[!] Timeout. Retransmitindo pacote {seq_num}...")

        # ---- Esgotou as tentativas: o servidor fara o rollback ----
        if not ack_recebido:
            print(f"[X] Falha: pacote {seq_num} nao confirmado em {MAX_TENTATIVAS} tentativas. Abortando.")
            break

        # ---- ACK ok: avanca para o proximo pacote -----------
        seq_num += 1
        if flag == 1:
            print("[*] Transferencia concluida com sucesso!")
            break

# ---- Questao 10.1: para o cronometro e calcula a vazao ------
fim = time.perf_counter()
decorrido = fim - inicio
# Mbps = (bytes * 8 bits) / (segundos * 1.000.000)
mbps = (tamanho_arquivo * 8) / (decorrido * 1_000_000) if decorrido > 0 else 0.0
print(f"[*] {tamanho_arquivo} bytes em {decorrido:.3f}s  ->  {mbps:.3f} Mbps")
sock.close()
