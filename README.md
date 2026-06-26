# Transferência confiável de arquivos sobre UDP

Trabalho da disciplina **ADS0030 — Programação em Ambiente de Rede** (UFCA).

Implementação de um sistema cliente/servidor que transfere um arquivo PDF sobre
**UDP**, reconstruindo na mão a confiabilidade que o TCP oferece, através do
protocolo **Stop-and-Wait**: numeração de pacotes, confirmação por ACK, timeout e
retransmissão.

## Estrutura

```
.
├── entrega/
│   ├── servidor.py          # Receptor: recebe os pacotes e monta recebido.pdf
│   ├── cliente.py           # Enviador: lê o PDF e envia em pacotes de 1024 bytes
│   ├── GUIA_ENTREGA.md      # Checklist e instruções de execução
│   ├── roteiro_video.md     # Roteiro + falas para o vídeo de demonstração
│   └── respostas_pesquisa.md
└── material_professor/      # Material original do enunciado (imagens)
```

## Como rodar

Coloque um arquivo PDF na pasta `entrega/`, ajuste `NOME_ARQUIVO` no `cliente.py`
e abra dois terminais:

```bash
cd entrega
python3 servidor.py   # Terminal 1
python3 cliente.py    # Terminal 2
```

O arquivo recebido é salvo como `recebido.pdf`. Para conferir a integridade:

```bash
cmp meu_arquivo.pdf recebido.pdf && echo "Arquivos idênticos!"
```

## Demonstração de confiabilidade

No `servidor.py`, troque `SIMULAR_REDE_RUIM = False` por `True` para ativar o
simulador que descarta 30% dos pacotes. Mesmo com a perda, o arquivo chega íntegro
graças à retransmissão.

## Protocolo

Cada pacote tem um cabeçalho de **9 bytes** no formato `!IIB`:

| Campo      | Tipo            | Descrição                          |
|------------|-----------------|------------------------------------|
| `seq_num`  | uint32 (4 bytes)| Número de sequência do pacote      |
| `trans_id` | uint32 (4 bytes)| Identificador da transferência     |
| `flag`     | uint8  (1 byte) | 1 = último pacote, 0 = há mais     |
