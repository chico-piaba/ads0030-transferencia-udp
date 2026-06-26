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
├── entrega/                 # Versão ENXUTA (o que se submete no AVA)
│   ├── servidor.py          # Receptor: recebe pacotes, monta recebido.pdf, rollback
│   ├── cliente.py           # Emissor: envia com retransmissão, mede a vazão (Mbps)
│   ├── GUIA_ENTREGA.md
│   ├── roteiro_video.md
│   └── respostas_pesquisa.md
├── estudo/                  # Mesmas servidor.py/cliente.py, comentadas linha a linha
│   ├── servidor.py
│   └── cliente.py
├── material_professor/      # Enunciado original + imagens (codigo01..06)
└── contexto.md              # Enunciado completo (referência)
```

## Como rodar

Coloque uma imagem/PDF em `entrega/`, ajuste `NOME_ARQUIVO` no `cliente.py` e abra
dois terminais:

```bash
cd entrega
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
