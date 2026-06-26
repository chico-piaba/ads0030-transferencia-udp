import socket
import struct
import os
import random
import time

IP_DESTINO = "127.0.0.1"
PORTA_DESTINO = 8080
NOME_ARQUIVO = "foto.jpg"           # coloque uma imagem/PDF real nesta pasta
TAMANHO_PAYLOAD = 1024
FORMATO_CABECALHO = "!IIB"          # seq_num (I) + trans_id (I) + flag (B) = 9 bytes
FORMATO_ACK = "!I"                  # mesmo formato de ACK do servidor
TAMANHO_ACK = struct.calcsize(FORMATO_ACK)

# Subimos de 5 para 15 tentativas: com 30% de perda nos DOIS sentidos (dados + ACK),
# cada tentativa tem ~49% de sucesso, entao poucas tentativas as vezes nao bastam.
MAX_TENTATIVAS = 15

# Tarefa B: simulador de rede ruim (descarta ACKs na recepcao do cliente)
SIMULAR_REDE_RUIM = True
CHANCE_PERDA = 0.3

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(1.0)                # timeout do Stop-and-Wait

trans_id = random.randint(1000, 9999)
seq_num = 0
print(f"[*] Enviando {NOME_ARQUIVO} (transacao {trans_id})")

tamanho_arquivo = os.path.getsize(NOME_ARQUIVO)
inicio = time.perf_counter()        # Questao 10.1: cronometro da transferencia

with open(NOME_ARQUIVO, "rb") as arquivo:
    while True:
        pedaco = arquivo.read(TAMANHO_PAYLOAD)
        flag = 1 if len(pedaco) < TAMANHO_PAYLOAD else 0
        pacote = struct.pack(FORMATO_CABECALHO, seq_num, trans_id, flag) + pedaco

        ack_recebido = False
        tentativas = 0
        while not ack_recebido and tentativas < MAX_TENTATIVAS:
            try:
                sock.sendto(pacote, (IP_DESTINO, PORTA_DESTINO))
                print(f"[>] Pacote {seq_num} enviado (tentativa {tentativas+1}). Aguardando ACK...")
                dados_ack, _ = sock.recvfrom(TAMANHO_ACK)

                # Tarefa B: simula perda do ACK -> reusa o caminho de timeout
                if SIMULAR_REDE_RUIM and random.random() < CHANCE_PERDA:
                    print("[SIMULACAO] ACK perdido na rede...")
                    raise socket.timeout

                ack_num = struct.unpack(FORMATO_ACK, dados_ack)[0]
                if ack_num == seq_num:
                    ack_recebido = True
                    print(f"[<] ACK {ack_num} recebido.")
            except socket.timeout:
                tentativas += 1
                print(f"[!] Timeout. Retransmitindo pacote {seq_num}...")

        if not ack_recebido:
            print(f"[X] Falha: pacote {seq_num} nao confirmado em {MAX_TENTATIVAS} tentativas. Abortando.")
            break

        seq_num += 1
        if flag == 1:
            print("[*] Transferencia concluida com sucesso!")
            break

fim = time.perf_counter()
decorrido = fim - inicio
mbps = (tamanho_arquivo * 8) / (decorrido * 1_000_000) if decorrido > 0 else 0.0
print(f"[*] {tamanho_arquivo} bytes em {decorrido:.3f}s  ->  {mbps:.3f} Mbps")
sock.close()
