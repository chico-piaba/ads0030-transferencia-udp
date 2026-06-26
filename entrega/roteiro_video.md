# Roteiro do vídeo — Estudo Guiado 01 (SRTP sobre UDP) — ADS0030

> **Limite: 7 minutos.** Grave a tela com microfone. O enunciado (Seção 11) exige
> obrigatoriamente, dentro do vídeo:
> 1. Respostas sucintas para TODAS as perguntas ❓ (4.1, 4.2, 4.3, 5.1, 8.1).
> 2. Explicar o código: **modularização**, **lógica de Retry** e **Controle de
>    Transação** (remoção do arquivo corrompido).
> 3. Transferir uma **imagem** (ex.: foto.jpg) e **abri-la no lado do servidor**
>    para provar que não corrompeu.
> 4. A simulação de perda (30%) **DEVE estar ligada** — mostrar "Timeout" e
>    "Retransmissão" no terminal do emissor.
> 5. No fim: **fechar o cliente no meio** (Ctrl+C) e mostrar o servidor, após 10s,
>    **apagando o arquivo incompleto**. Mostrar a pasta provando a remoção.

> Antes de gravar: deixe `SIMULAR_REDE_RUIM = True` nos dois arquivos e use uma
> imagem pequena (uns 20–60 KB) para o vídeo não ficar lento.

---

## Bloco 1 — Abertura + Pesquisas (≈ 1min30)
**`[fala]`** "Olá, sou [NOME], matrícula [xxxx]. Implementei o SRTP, um protocolo
de transferência confiável de arquivos sobre UDP. Antes, respondo as pesquisas:"
- **4.1:** payload seguro na internet é ~508 bytes (MTU mínimo do IPv4); evita
  fragmentação, por isso uso pedaços de até 1024 bytes na LAN.
- **4.2:** Stop-and-Wait é enviar um pacote e esperar o ACK antes do próximo; se o
  ACK não vem, retransmite.
- **4.3:** a ordem de bytes da rede é Big-Endian — uso o `!` no struct.
- **5.1:** base64 para canais de texto (JSON, e-mail); struct.pack para
  cabeçalhos binários eficientes, que é o meu caso.
- **8.1:** dá para testar pela internet, mas precisa de IP público, port
  forwarding e firewall liberado, por causa do NAT.

## Bloco 2 — Explicação do código (≈ 1min30)  [EXIGÊNCIA 2]
**`[mostre os arquivos servidor.py e cliente.py]`**
- **Modularização:** "Separei em dois programas — `cliente.py` (emissor) e
  `servidor.py` (receptor) — que compartilham o mesmo formato de cabeçalho `!IIB`
  de 9 bytes: número de sequência, ID da transação e a flag de último pacote."
- **Lógica de Retry `[aponte o while not ack_recebido...]`:** "Aqui está o coração:
  envio o pacote e espero o ACK por 1 segundo. Se dá `socket.timeout`, eu conto a
  tentativa e retransmito, até 15 vezes."
- **Controle de Transação `[aponte o except socket.timeout do servidor]`:** "O
  servidor tem timeout de 10 segundos. Se o cliente some, ele apaga o arquivo
  incompleto do disco com `os.remove`, pra não deixar arquivo corrompido."

## Bloco 3 — Demo da transferência com PERDA ligada (≈ 2min)  [EXIGÊNCIAS 3 e 4]
**`[terminal 1]`** `python3 servidor.py`
**`[terminal 2]`** `python3 cliente.py`
**`[fala]`** "Com a simulação de 30% de perda ligada nos dois lados, vejam: o
servidor descarta pacotes, o cliente dá Timeout e Retransmite. Mesmo assim..."
- Aponte na tela: `[SIMULACAO] Pacote perdido`, `[!] Timeout. Retransmitindo`,
  `[SIMULACAO] ACK perdido`.
- Ao terminar: **abra a imagem `recebido.pdf` no lado do servidor** e mostre que
  ela abre perfeitamente. "Mesmo com toda a perda, a imagem chegou íntegra."
  *(Opcional: rode `cmp foto.jpg recebido.pdf` mostrando que são idênticas.)*

## Bloco 4 — Demo do Rollback (≈ 1min30)  [EXIGÊNCIA 5]
**`[fala]`** "Agora mostro o controle de transação. Vou iniciar de novo e, no meio,
fechar o cliente de propósito."
- `python3 servidor.py` / `python3 cliente.py`
- Após alguns pacotes, **aperte Ctrl+C no cliente** (ou feche o terminal).
- Aponte o terminal do servidor parado, aguardando.
- Após 10 segundos, mostre: `[X] 10s sem pacotes... Abortando` e
  `[X] Arquivo incompleto 'recebido.pdf' removido do disco.`
- **Abra a pasta** (ou rode `ls`) provando que `recebido.pdf` **não existe mais**.
- **`[fala de fechamento]`** "Resumindo: SRTP sobre UDP, com numeração, ACK,
  timeout, retransmissão e rollback de transações incompletas. Obrigado!"

---

### Checklist antes de gravar
- [ ] Imagem real na pasta `entrega/` + `NOME_ARQUIVO` ajustado no `cliente.py`.
- [ ] `SIMULAR_REDE_RUIM = True` nos DOIS arquivos.
- [ ] Ensaiar uma vez (a perda é aleatória; rode até pegar uma boa sequência).
- [ ] Terminal com fonte grande e áudio testado.
- [ ] Cronometrar: tem que caber em 7 minutos.
