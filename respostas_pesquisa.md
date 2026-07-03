# Respostas — Estudo Guiado 01 (SRTP sobre UDP) — ADS0030

> Reescreva com SUAS palavras antes de entregar. O conteúdo abaixo está correto
> e completo, pronto para você adaptar. Itens marcados `[MEDIR]` dependem do seu
> teste real.

---

# Seção 0 / 4 — Pesquisa Inicial

## ❓ Pesquisa 4.1 — Tamanho máximo seguro de um pacote UDP (sem fragmentação)

- Na **internet**, o tamanho seguro de **payload UDP** para não sofrer
  fragmentação é de cerca de **508 bytes**. Esse número vem do MTU mínimo
  garantido do IPv4 (576 bytes) menos o cabeçalho IP (20) e o cabeçalho UDP (8).
- Em **rede local Ethernet**, o MTU típico é **1500 bytes**, o que permite um
  payload UDP de até ~**1472 bytes**.
- **Por que evitar fragmentação?** Se um datagrama UDP é quebrado em vários
  fragmentos IP e **um único fragmento se perde**, o datagrama **inteiro** é
  descartado. Isso aumenta muito a taxa de perda efetiva.
- **Como isso afeta o tamanho do pedaço lido do arquivo?** Por isso lemos o
  arquivo em pedaços de no máximo **1024 bytes** de payload. Com os 9 bytes de
  cabeçalho, o pacote tem 1033 bytes — cabe folgado no MTU de 1500 da LAN. Para
  uso real pela internet, o ideal seria reduzir o payload para ~500 bytes.

## ❓ Pesquisa 4.2 — O que é Stop-and-Wait (com diagrama)

É o ARQ mais simples: o emissor envia **um** pacote e **espera o ACK** antes de
enviar o próximo. Se o ACK não chega dentro do timeout, ele **retransmite**.

Diagrama de sequência (caso de pacote perdido):

```
 CLIENTE                         SERVIDOR
   |  --- Pacote SeqNum=0 ------->  |  (recebe, grava)
   |  <-------- ACK 0 ------------  |
   |  --- Pacote SeqNum=1 ---X      |  (PACOTE PERDIDO na rede)
   |     (espera 1s... timeout!)    |
   |  --- Pacote SeqNum=1 ------->  |  (recebe, grava)
   |  <-------- ACK 1 ------------  |
   |  --- Pacote SeqNum=2 ------->  |  (recebe, grava)
   |  <---X---- ACK 2               |  (ACK PERDIDO na rede)
   |     (espera 1s... timeout!)    |
   |  --- Pacote SeqNum=2 ------->  |  (DUPLICATA: não grava, só re-ACK)
   |  <-------- ACK 2 ------------  |
```

## ❓ Pesquisa 4.3 — Ordem de bytes padrão da rede (Network Byte Order)

É **Big-Endian** (o byte mais significativo primeiro). No `struct`, o símbolo
`!` no formato (`"!IIB"`) já garante essa ordem, independente de a máquina ser
little-endian (como a maioria dos PCs x86).

## ❓ Pesquisa 5.1 — Quando usar base64 vs struct.pack

- **base64:** quando você precisa enviar dados binários por um canal que só
  aceita **texto** (JSON, e-mail, URL, XML). Custo: aumenta o tamanho em ~33%.
- **struct.pack:** quando você controla os dois lados e quer **eficiência** —
  monta campos binários de tamanho fixo (cabeçalhos de protocolo) sem desperdício.
  É o caso deste trabalho: o cabeçalho de 9 bytes (`!IIB`) é montado com `pack`.

## ❓ Pesquisa 8.1 — Dá para testar pela internet?

Sim, mas exige configuração extra (não funciona "de graça" como no `127.0.0.1`):

1. **IP público + NAT:** o roteador compartilha um único IP público; o cliente
   externo não enxerga o IP privado do servidor.
2. **Port forwarding:** criar uma regra no roteador mandando o UDP:8080 para a
   máquina interna do servidor.
3. **Firewall:** liberar a porta UDP 8080 no SO e, às vezes, no provedor.
4. **Perda e MTU reais:** pela internet a perda é real e pacotes acima do MTU
   podem ser descartados — daí a importância do payload pequeno (Pesquisa 4.1).

---

# Seção 10 — Questões para Análise

## 10.1 — Taxa de transferência efetiva (e por que Stop-and-Wait é ineficiente)

- **Valor medido `[MEDIR]`:** rode com `SIMULAR_REDE_RUIM = False` e anote a linha
  final do cliente (`... -> X Mbps`). Em `127.0.0.1` costuma dar **dezenas de
  Mbps** (nos meus testes, ~50 Mbps em arquivos pequenos).
- **Por que é ineficiente?** O Stop-and-Wait gasta **1 RTT (ida e volta) por
  pacote**, ficando ocioso enquanto espera cada ACK. A vazão fica limitada a
  ~`payload / RTT`, sem aproveitar a largura de banda disponível.
- **Arquivos grandes vs pequenos `[MEDIR]`:** em arquivos muito pequenos o tempo é
  dominado pelo custo fixo de iniciar/finalizar; em arquivos grandes (>100 MB), a
  ineficiência do "espera-a-cada-pacote" aparece de forma acumulada — a vazão
  tende a um valor estável e baixo perto de `payload/RTT`.

## 10.2 — Por que lidar com pacotes duplicados se o TCP nunca os repete?

O TCP **trata duplicatas internamente** e nunca as entrega à aplicação. No nosso
protocolo sobre UDP, **nós** somos a camada de confiabilidade, então temos que
tratar isso na mão.

**Situação hipotética (cliente reenvia SeqNum=5 já salvo):**
1. Cliente envia `SeqNum=5`. O servidor recebe, **grava no disco** e envia `ACK 5`.
2. O `ACK 5` **se perde** na volta.
3. O cliente, sem receber o ACK, estoura o timeout e **retransmite o SeqNum=5**.
4. O servidor recebe o `SeqNum=5` de novo, mas `seq_esperado` já é 6. Ele percebe a
   **duplicata** (`seq_num != seq_esperado`), **não grava de novo** (evita
   corromper o arquivo) e apenas **reenvia o ACK** para destravar o cliente.

## 10.3 — Técnica para substituir o Stop-and-Wait: Janela Deslizante

A **Janela Deslizante (Sliding Window)** permite ter **vários pacotes em trânsito
ao mesmo tempo**, sem esperar o ACK de cada um.

- O emissor pode enviar até **N** pacotes (o tamanho da janela) antes de precisar
  de uma confirmação.
- Conforme os ACKs chegam, a **janela "desliza"** para frente, liberando o envio
  de novos pacotes.
- Isso mantém o canal **sempre ocupado**, aumentando muito a vazão (é o que o TCP
  usa). Variantes comuns: **Go-Back-N** (retransmite tudo a partir do pacote
  perdido) e **Selective Repeat** (retransmite só o que faltou).
