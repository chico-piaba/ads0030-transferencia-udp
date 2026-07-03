# SRTP — Transferência confiável de arquivos sobre UDP

Trabalho da disciplina **ADS0030 — Programação em Ambiente de Rede** (UFCA) —
*Estudo Guiado 01*.

Implementação do **SRTP** (Simple Reliable Transfer Protocol): um sistema
cliente/servidor que transfere um arquivo (imagem/PDF) sobre **UDP**,
reconstruindo na mão a confiabilidade que o TCP oferece. Inclui numeração de
pacotes, ACK, timeout, retransmissão (Stop-and-Wait), controle de transação com
rollback e um simulador de rede ruim.

## Estrutura

```
.
├── servidor.py           # Receptor: recebe pacotes, monta recebido.pdf, rollback
├── cliente.py            # Emissor: envia com retransmissão, mede a vazão (Mbps)
└── respostas_pesquisa.md # Respostas das Pesquisas e Análises
```

> Os códigos `servidor.py`/`cliente.py` estão **comentados linha a linha** para
> facilitar o estudo e a defesa no vídeo.

## Como rodar

Coloque uma imagem/PDF na pasta, ajuste `NOME_ARQUIVO` no `cliente.py` e abra
dois terminais:

```bash
python3 servidor.py   # Terminal 1
python3 cliente.py    # Terminal 2
```

O arquivo recebido é salvo como `recebido.pdf`. Conferir integridade:

```bash
cmp foto.jpg recebido.pdf && echo "Arquivos idênticos!"
```

## Funcionalidades

- **Stop-and-Wait com retransmissão:** envia 1 pacote, espera o ACK; sem ACK em
  1s, retransmite (até 15 tentativas).
- **Tarefa A — Rollback:** o servidor aborta após 10s sem pacotes e apaga o
  arquivo incompleto (`os.remove`).
- **Tarefa B — Simulador de rede ruim:** 30% de perda no servidor (dados) e no
  cliente (ACKs). Ligue/desligue com `SIMULAR_REDE_RUIM`.
- **Medição de vazão (Q10.1):** o cliente reporta a taxa em Mbps ao final.

## Protocolo SRTP

**Pacote de dados (Cliente → Servidor):** cabeçalho de **9 bytes** `!IIB` + payload.

| Campo      | Tipo            | Descrição                          |
|------------|-----------------|------------------------------------|
| `seq_num`  | uint32 (4 bytes)| Número de sequência do pacote      |
| `trans_id` | uint32 (4 bytes)| Identificador da transferência     |
| `flag`     | uint8  (1 byte) | 1 = último pacote, 0 = há mais     |
| payload    | ≤ 1024 bytes    | Pedaço do arquivo                  |

**ACK (Servidor → Cliente):** `!I` — apenas o número de sequência confirmado.
