# =============================================================
#  SERVIDOR UDP - Receptor de arquivos (Stop-and-Wait)
#  Disciplina: ADS0030 - Programacao em Ambiente de Rede
# =============================================================
#  Junta o codigo das imagens "codigo02" (inicio) + "codigo03"
#  (esqueleto com TODOs) + "codigo6" (simulador de rede ruim).
#  Os TODOs do enunciado estao preenchidos e marcados com [FEITO].
# =============================================================

import socket
import struct
import random   # necessario para o "simulador de rede ruim" (codigo6)

# --- Configuracoes da rede -----------------------------------
IP = ""                       # "" = escuta em todas as interfaces da maquina
PORTA = 8080

# --- Formato do cabecalho ------------------------------------
# "!IIB" -> Network Byte Order (Big-Endian)
#   I  = Unsigned Int  (4 bytes) -> numero de sequencia (seq_num)
#   I  = Unsigned Int  (4 bytes) -> id da transacao     (trans_id)
#   B  = Unsigned Char (1 byte)  -> flag (1 = ultimo pacote, 0 = tem mais)
FORMATO_CABECALHO = "!IIB"
TAMANHO_CABECALHO = struct.calcsize(FORMATO_CABECALHO)   # deve ser 9

# Formato do ACK que o servidor devolve ao cliente:
#   "!II" -> seq_num confirmado + id da transacao
FORMATO_ACK = "!II"

# --- Chave para ligar/desligar o "simulador de rede ruim" ----
SIMULAR_REDE_RUIM = False     # mude para True para testar a retransmissao
CHANCE_PERDA = 0.3            # 30% de chance de "perder" o pacote

# --- Criando o socket UDP ------------------------------------
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORTA))
print(f"[*] Servidor UDP aguardando arquivos em {IP or '0.0.0.0'}:{PORTA}...")
print(f"[*] Tamanho do cabecalho: {TAMANHO_CABECALHO} bytes")

# --- Estado da transferencia ---------------------------------
seq_esperado = 0                                  # proximo seq_num que esperamos
arquivo_destino = open("recebido.pdf", "wb")      # arquivo que sera montado
transacao_atual = None                            # trava na 1a transacao que chegar

try:
    while True:
        # ---- Recebendo dados (buffer maior que o MTU) -------
        pacote, endereco_cliente = sock.recvfrom(2048)

        # ---- [codigo6] SIMULADOR DE REDE RUIM ---------------
        # Joga fora 30% dos pacotes ANTES de processar, fingindo
        # que eles se perderam na rede. Isso forca o cliente a
        # estourar o timeout e retransmitir.
        if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:
            print("[SIMULACAO] Ops, pacote perdido na rede...")
            continue   # ignora: simula que o pacote nunca chegou

        # ---- Separar o cabecalho do payload -----------------
        cabecalho_bytes = pacote[:TAMANHO_CABECALHO]
        payload = pacote[TAMANHO_CABECALHO:]

        # ---- Desempacotar o cabecalho -----------------------
        seq_num, trans_id, flag = struct.unpack(FORMATO_CABECALHO, cabecalho_bytes)

        # ---- Primeiro pacote: registramos o trans_id --------
        if transacao_atual is None:
            transacao_atual = trans_id
            print(f"[*] Nova transferencia iniciada (ID {trans_id})")

        # ---- Ignora pacotes de outra transacao --------------
        if trans_id != transacao_atual:
            continue   # ignora pacotes alienigenas

        # ===========================================================
        #  [FEITO] TODO: tratar o pacote (gravar + confirmar com ACK)
        # ===========================================================
        if seq_num == seq_esperado:
            # Pacote certo, na ordem certa -> grava no arquivo
            arquivo_destino.write(payload)
            print(f"[+] Pacote {seq_num} gravado ({len(payload)} bytes).")
            seq_esperado += 1

            # Envia ACK confirmando ESTE seq_num
            ack = struct.pack(FORMATO_ACK, seq_num, trans_id)
            sock.sendto(ack, endereco_cliente)

            # Se for o ultimo pacote (flag == 1), encerramos
            if flag == 1:
                print("[*] Ultimo pacote recebido. Transferencia concluida!")
                break
        else:
            # Pacote duplicado/fora de ordem (ex.: o ACK anterior se
            # perdeu e o cliente reenviou). Reenviamos o ACK do ultimo
            # pacote que ja gravamos corretamente, para destravar o cliente.
            print(f"[~] Pacote {seq_num} ignorado (esperava {seq_esperado}). Reenviando ACK.")
            ack = struct.pack(FORMATO_ACK, seq_esperado - 1, trans_id)
            sock.sendto(ack, endereco_cliente)

finally:
    arquivo_destino.close()
    sock.close()
    print("[*] Servidor finalizado. Arquivo salvo como 'recebido.pdf'.")
