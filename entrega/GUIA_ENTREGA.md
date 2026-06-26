# Guia de entrega — Estudo Guiado 01 (SRTP sobre UDP) — ADS0030

## O que é o trabalho
Transferência confiável de um arquivo (imagem/PDF) sobre **UDP**, implementando o
protocolo **SRTP** (Simple Reliable Transfer Protocol) com Stop-and-Wait:
numeração de pacotes, ACK, timeout, retransmissão, controle de transação e
simulador de rede ruim.

## Arquivos (pasta `entrega/`)
| Arquivo | O que é |
|---------|---------|
| `servidor.py` | Receptor — recebe os pacotes, monta `recebido.pdf`, faz rollback. |
| `cliente.py` | Emissor — lê o arquivo, envia com retransmissão, mede a vazão. |
| `roteiro_video.md` | Roteiro do vídeo (máx 7 min) com as 5 exigências da Seção 11. |
| `respostas_pesquisa.md` | Respostas das Pesquisas 4.1–8.1 e das Questões 10.1–10.3. |
| `GUIA_ENTREGA.md` | Este guia. |

> A pasta `../estudo/` tem as **mesmas** `servidor.py`/`cliente.py` porém cheias de
> comentários didáticos. Estude por lá; **entregue** os arquivos enxutos de `entrega/`.

## ✅ Tarefas do enunciado — TODAS implementadas
- [x] Protocolo SRTP: cabeçalho `!IIB` (9 bytes) + payload (≤1024 B). ACK = `!I`.
- [x] Servidor: recepção em ordem, gravação e ACK por pacote, ignora duplicatas.
- [x] Cliente: Stop-and-Wait com timeout de 1s e retransmissão (até 15 tentativas).
- [x] **Tarefa A (Rollback):** servidor com timeout de 10s; se o cliente some,
      apaga o `recebido.pdf` incompleto com `os.remove()`.
- [x] **Tarefa B (Perda):** simulador de 30% de perda no **servidor** (dados) e no
      **cliente** (ACKs).
- [x] **Questão 10.1:** cliente mede a vazão em Mbps com `time.perf_counter()`.
- [x] Respostas das Pesquisas (4.1, 4.2, 4.3, 5.1, 8.1) e Análises (10.1–10.3).

## ✅ Checklist do que VOCÊ ainda faz
1. [ ] Colocar uma **imagem real** (`foto.jpg`) em `entrega/` e ajustar
   `NOME_ARQUIVO` no `cliente.py`.
2. [ ] Medir a vazão real (Questão 10.1): rodar com `SIMULAR_REDE_RUIM = False` e
   anotar os Mbps (teste com arquivo grande e pequeno).
3. [ ] Reescrever as respostas com suas palavras (`respostas_pesquisa.md`).
4. [ ] Gravar o vídeo (`roteiro_video.md`) — máx 7 min, perda LIGADA, mostrar o
   rollback no final.
5. [ ] Compactar a pasta `entrega/` para submeter no AVA.

## Como rodar
Dois terminais dentro de `entrega/`:
```bash
python3 servidor.py   # Terminal 1
python3 cliente.py    # Terminal 2
```
- **Demo de perda/retransmissão:** deixe `SIMULAR_REDE_RUIM = True` (já é o padrão).
- **Medir vazão (Q10.1):** mude para `SIMULAR_REDE_RUIM = False` nos dois.
- **Demo de rollback:** rode os dois e feche o cliente com `Ctrl+C` no meio;
  o servidor apaga o arquivo após 10s.

## Como o protocolo funciona (resumo)
1. Cliente lê o arquivo em pedaços de **1024 bytes**.
2. Cada pacote = **cabeçalho 9 bytes** (`!IIB`: seq_num, trans_id, flag) + payload.
3. Stop-and-Wait: envia 1 pacote, espera o **ACK** (`!I`); sem ACK em 1s,
   retransmite (até 15×).
4. Servidor grava em ordem (`seq_esperado`), confirma com ACK, ignora duplicatas.
5. `flag = 1` marca o último pacote. Se o cliente some, o servidor faz **rollback**.
