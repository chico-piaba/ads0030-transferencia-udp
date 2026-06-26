# Roteiro do vídeo de demonstração — ADS0030

> Duração-alvo: **4 a 6 minutos**. Grave a tela (OBS / gravador do sistema) com
> microfone. Fale com naturalidade — os tópicos abaixo são o que mostrar/dizer.

---

## 0. Abertura (15s)
- "Olá, sou [seu nome], matrícula [xxxx]. Este é o trabalho de Programação em
  Ambiente de Rede: uma transferência de arquivos confiável sobre UDP."
- Mostre os arquivos na pasta: `servidor.py`, `cliente.py`, o PDF de origem.

## 1. O problema (40s)
- "UDP é rápido mas **não garante entrega** nem ordem. Eu implementei na mão a
  confiabilidade, usando o protocolo **Stop-and-Wait**."
- Explique o cabeçalho de 9 bytes (`!IIB`): número de sequência, ID da transação
  e a flag de último pacote. Abra `servidor.py` e aponte a linha do
  `FORMATO_CABECALHO`.

## 2. Mostrar o código-chave (90s)
- **Cliente** (`cliente.py`): aponte o loop `while not ack_recebido and tentativas < MAX`.
  "Aqui está o coração: envio o pacote, espero o ACK. Se der `socket.timeout`,
  eu retransmito até 5 vezes."
- **Servidor** (`servidor.py`): aponte o `if seq_num == seq_esperado:` →
  "gravo o pedaço no arquivo e devolvo um ACK confirmando."
- Mencione o tratamento de duplicata (o `else`): "se um ACK se perde, o cliente
  reenvia; eu detecto a duplicata e re-confirmo, sem corromper o arquivo."

## 3. Demonstração 1 — rede normal (60s)
- Terminal 1: `python3 servidor.py`
- Terminal 2: `python3 cliente.py`
- Mostre os ACKs chegando em sequência e a mensagem "Transferência concluída".
- Abra o `recebido.pdf` para provar que abre corretamente. (Opcional: rode
  `cmp meu_arquivo.pdf recebido.pdf` para mostrar que são idênticos.)

## 4. Demonstração 2 — rede ruim / retransmissão (90s)  ← PARTE MAIS IMPORTANTE
- No `servidor.py`, mude `SIMULAR_REDE_RUIM = False` para `True`. Explique:
  "Agora o servidor descarta 30% dos pacotes de propósito, simulando uma rede ruim."
- Rode de novo servidor + cliente.
- Aponte na tela: `[SIMULACAO] Ops, pacote perdido...` no servidor e
  `[!] Timeout. Retransmitindo...` no cliente.
- "Mesmo perdendo pacotes, o arquivo final chega **íntegro**. É isso que prova
  que minha camada de confiabilidade funciona."
- Mostre que o `recebido.pdf` continua abrindo / idêntico.

## 5. Pesquisa e fechamento (45s)
- Responda em voz alta a Pesquisa 8.1: "Dá para testar pela internet? Sim, mas
  precisa de IP público, port forwarding e liberação de firewall, porque o NAT
  esconde o IP interno do servidor." (resumo de `respostas_pesquisa.md`)
- "Resumindo: implementei Stop-and-Wait sobre UDP, com numeração de pacotes,
  ACKs, timeout e retransmissão. Obrigado."

---

### Checklist antes de gravar
- [ ] Colocar um PDF real na pasta e ajustar `NOME_ARQUIVO` no `cliente.py`.
- [ ] Testar tudo UMA vez antes de gravar (para não travar na hora).
- [ ] Deixar `SIMULAR_REDE_RUIM = False` para a demo 1 e `True` para a demo 2.
- [ ] Áudio funcionando e tela legível (fonte do terminal grande).

---

# 🎙️ FALAS PRONTAS (leia em voz alta enquanto grava)

> Texto em linguagem falada. Leia com calma, do seu jeito. `[AÇÃO]` = o que fazer
> na tela naquele momento. Total falando devagar: ~5 minutos.

**`[AÇÃO: tela mostrando a pasta com os arquivos]`**
"Olá! Eu sou o(a) [SEU NOME], da disciplina de Programação em Ambiente de Rede.
Neste vídeo eu vou demonstrar um sistema que transfere um arquivo PDF de um
computador para outro usando o protocolo UDP. O detalhe é que o UDP, sozinho, não
garante que os dados cheguem — então eu tive que implementar a confiabilidade na
mão."

**`[AÇÃO: abrir o servidor.py e apontar a linha do FORMATO_CABECALHO]`**
"A base de tudo é este cabeçalho de nove bytes. Cada pacote que eu envio carrega
três informações: um número de sequência, pra saber a ordem; um ID da transação,
pra identificar essa transferência; e uma flag, que vale um quando é o último
pacote. Tudo isso empacotado em binário com o módulo struct."

**`[AÇÃO: rolar até o loop while no cliente.py]`**
"Aqui no cliente está o coração do protocolo, que se chama Stop-and-Wait. Eu envio
um pacote e fico esperando uma confirmação, que a gente chama de ACK. Se essa
confirmação não chega em um segundo, o socket dá timeout e eu reenvio o mesmo
pacote, tentando até cinco vezes."

**`[AÇÃO: apontar o if seq_num == seq_esperado no servidor.py]`**
"E aqui no servidor é o outro lado: quando o pacote certo chega, eu gravo o pedaço
no arquivo e devolvo o ACK confirmando. Se um pacote chegar repetido, eu percebo e
só reenvio a confirmação, sem corromper o arquivo."

**`[AÇÃO: rodar 'python3 servidor.py' no terminal 1]`**
"Agora a demonstração. Primeiro eu subo o servidor... ele fica aguardando."

**`[AÇÃO: rodar 'python3 cliente.py' no terminal 2]`**
"E aqui eu rodo o cliente. Repare na tela: cada pacote é enviado e logo vem o ACK
correspondente, em sequência, até a mensagem de transferência concluída."

**`[AÇÃO: abrir o recebido.pdf]`**
"E o arquivo que chegou abre normalmente — é uma cópia perfeita do original."

**`[AÇÃO: editar servidor.py, trocar SIMULAR_REDE_RUIM para True]`**
"Agora vem a parte mais importante, que prova que o meu protocolo realmente
funciona. Eu vou ligar um simulador de rede ruim: o servidor vai jogar fora,
de propósito, trinta por cento dos pacotes, como se a rede estivesse perdendo
dados."

**`[AÇÃO: rodar servidor e cliente de novo, apontar as mensagens de perda/timeout]`**
"Olha o que acontece: o servidor avisa que perdeu um pacote, o cliente dá timeout
e retransmite automaticamente. Mesmo com toda essa perda, o arquivo final chega
completo e íntegro. Isso é exatamente a confiabilidade que o TCP faria — só que
aqui eu construí na mão, em cima do UDP."

**`[AÇÃO: pode mostrar o recebido.pdf abrindo de novo]`**
"Sobre a pergunta de pesquisa, se daria pra testar isso pela internet: daria sim,
mas precisaria de IP público, redirecionamento de porta no roteador e liberação no
firewall, porque o NAT esconde o endereço interno da máquina do servidor."

**`[AÇÃO: tela final / encerramento]`**
"Pra fechar: eu implementei o protocolo Stop-and-Wait sobre o UDP, com numeração
de pacotes, confirmação por ACK, timeout e retransmissão. Era isso, muito
obrigado(a)!"
