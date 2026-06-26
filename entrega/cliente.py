# =============================================================
#  CLIENTE UDP - Enviador de arquivos (Stop-and-Wait)
#  Disciplina: ADS0030 - Programacao em Ambiente de Rede
# =============================================================
#  Junta o codigo das imagens "codigo04" (inicio) + "codigo05"
#  (loop de envio com retransmissao). Os TODOs estao preenchidos.
# =============================================================
#
#  Como testar:
#   1) teste primeiro localmente na sua maquina (IP 127.0.0.1)
#   2) depois pode testar com uma VM ou conteiner no seu computador
#   3) Pesquisa 8.1: sera possivel testar pela internet? (veja
#      respostas_pesquisa.md)
# =============================================================

import socket
import struct
import os
import random

# --- Configuracoes -------------------------------------------
IP_DESTINO = "127.0.0.1"      # IP do servidor (localhost para teste local)
PORTA_DESTINO = 8080

# Coloque um PDF real na mesma pasta e ajuste o nome abaixo
# (ou renomeie o arquivo para "meu_arquivo.pdf").
NOME_ARQUIVO = "meu_arquivo.pdf"

TAMANHO_PAYLOAD = 1024        # quantos bytes de arquivo por pacote
FORMATO_CABECALHO = "!IIB"    # mesmo formato do servidor!
FORMATO_ACK = "!II"           # mesmo formato de ACK do servidor!
TAMANHO_ACK = struct.calcsize(FORMATO_ACK)

# --- Socket UDP ----------------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Timeout: se o recvfrom (espera do ACK) demorar mais de 1 segundo,
# levanta uma excecao socket.timeout -> sinal para retransmitir.
sock.settimeout(1.0)

# trans_id identifica esta transferencia inteira (todos os pacotes usam)
trans_id = random.randint(1000, 9999)
seq_num = 0

print(f"[*] Iniciando transferencia de {NOME_ARQUIVO}")
print(f"[*] ID da Transacao: {trans_id}")

MAX_TENTATIVAS = 5

with open(NOME_ARQUIVO, "rb") as arquivo:
    while True:
        # ---- Ler um pedaco do arquivo -----------------------
        pedaco = arquivo.read(TAMANHO_PAYLOAD)

        # ---- Logica para descobrir se e o ultimo pacote -----
        # Se leu menos que o tamanho cheio (ou nada), e o ultimo.
        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD else 0

        # ---- Montar o pacote --------------------------------
        cabecalho = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag)
        pacote_completo = cabecalho + pedaco

        # ---- Loop do Stop-and-Wait (envio + retransmissao) --
        ack_recebido = False
        tentativas = 0

        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                # Enviar o pacote completo
                sock.sendto(pacote_completo, (IP_DESTINO, PORTA_DESTINO))
                print(f"[>] Pacote {seq_num} enviado. Aguardando ACK... "
                      f"(Tentativa {tentativas + 1})")

                # ---- [FEITO] TODO: esperar e validar o ACK ----
                dados_ack, _ = sock.recvfrom(TAMANHO_ACK)
                ack_seq, ack_trans = struct.unpack(FORMATO_ACK, dados_ack)

                # So aceita se for o ACK certo, da nossa transacao
                if ack_trans == trans_id and ack_seq == seq_num:
                    ack_recebido = True
                    print(f"[<] ACK {ack_seq} recebido.")

            except socket.timeout:
                # Nao chegou ACK a tempo -> conta tentativa e retransmite
                tentativas += 1
                print(f"[!] Timeout. Retransmitindo pacote {seq_num}...")

        # ---- Se esgotou as tentativas, aborta ---------------
        if not ack_recebido:
            print(f"[X] Falha: pacote {seq_num} nao confirmado apos "
                  f"{MAX_TENTATIVAS} tentativas. Abortando.")
            break

        # ---- ACK ok: avanca para o proximo pacote -----------
        seq_num += 1

        # ---- Se este era o ultimo pacote, terminamos --------
        if flag == 1:
            print("[*] Transferencia concluida com sucesso!")
            break

sock.close()
