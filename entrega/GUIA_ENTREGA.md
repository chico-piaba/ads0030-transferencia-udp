# Guia de entrega — ADS0030 Programação em Ambiente de Rede

## O que é o trabalho
Transferência confiável de um arquivo PDF sobre **UDP**, implementando o protocolo
**Stop-and-Wait** (numeração de pacotes, ACK, timeout e retransmissão).

## Arquivos desta pasta
| Arquivo | O que é |
|---------|---------|
| `servidor.py` | **PRONTO** — recebe o arquivo e monta `recebido.pdf`. TODOs preenchidos + simulador de rede ruim. |
| `cliente.py` | **PRONTO** — lê o PDF e envia em pacotes de 1024 bytes com retransmissão. |
| `roteiro_video.md` | Roteiro do vídeo de demonstração (4–6 min). |
| `respostas_pesquisa.md` | Respostas das perguntas de pesquisa (Pesquisa 8.1 etc.). |
| `codigo01..06.png` | Imagens originais do enunciado (material base). |

## ✅ Checklist do que VOCÊ tem que fazer

1. **[ ] Entender o código** (leia os comentários — o `servidor.py` e o
   `cliente.py` estão comentados linha a linha).
2. **[ ] Colocar um PDF real** na pasta e ajustar `NOME_ARQUIVO` no `cliente.py`
   (ou renomear o arquivo para `meu_arquivo.pdf`).
3. **[ ] Rodar o teste local** (instruções abaixo) e ver o arquivo chegar.
4. **[ ] Rodar o teste de rede ruim** (`SIMULAR_REDE_RUIM = True` no servidor) e
   ver a retransmissão funcionar.
5. **[ ] Responder as perguntas de pesquisa** com suas palavras
   (`respostas_pesquisa.md`).
6. **[ ] Gravar o vídeo** seguindo o `roteiro_video.md`.
7. **[ ] (Opcional/extra) Testar com VM ou contêiner** para mostrar comunicação
   entre máquinas diferentes.

## Como rodar (teste local)

Abra **dois terminais** nesta pasta.

**Terminal 1 (servidor):**
```bash
python3 servidor.py
```

**Terminal 2 (cliente):**
```bash
python3 cliente.py
```

O servidor cria `recebido.pdf`. Para conferir que ficou idêntico:
```bash
cmp meu_arquivo.pdf recebido.pdf && echo "Arquivos identicos!"
```

## Como demonstrar a confiabilidade (rede ruim)
No `servidor.py`, troque:
```python
SIMULAR_REDE_RUIM = False   →   SIMULAR_REDE_RUIM = True
```
Rode de novo. Você verá `[SIMULACAO] pacote perdido` no servidor e
`[!] Timeout. Retransmitindo` no cliente — e mesmo assim o arquivo chega íntegro.

## Como o protocolo funciona (resumo didático)
1. O cliente lê o PDF em pedaços de **1024 bytes**.
2. Cada pedaço vira um pacote = **cabeçalho de 9 bytes** (`!IIB`: seq_num,
   trans_id, flag) **+ payload**.
3. O cliente envia 1 pacote e **espera o ACK** (Stop-and-Wait).
4. Se o ACK não chega em 1s (`settimeout`), **retransmite** (até 5×).
5. O servidor grava os pacotes **em ordem** (`seq_esperado`) e devolve um ACK
   por pacote. Duplicatas são re-confirmadas sem gravar de novo.
6. A `flag = 1` marca o último pacote e encerra os dois lados.
