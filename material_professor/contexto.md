Estudo Guiado 01 - Criação de Protocolos: Transferência de Arquivos Confiável sobre UDP


1. Objetivos e Visão Geral        2

2. Conceitos Abordados        2

3. Pré-requisitos e Links Úteis        3

4. Pesquisa Inicial        3

5. A Biblioteca struct e Endianness        3

6. Especificação do Nosso Protocolo        5

7. Implementando o Servidor (Receptor)        6

8. Implementando o Cliente (Emissor)        9

9. Controle de Transação e Simulador de Redes Ruins        12

10. Questões para Análise        13

11. Formato de Entrega        1



1. Objetivos e Visão Geral
Em disciplinas anteriores, nós utilizamos o protocolo TCP quando precisávamos de conexões confiáveis (como no Chat TCP e no Servidor Web com Flask). O TCP abstrai toda a complexidade: ele garante que os dados cheguem em ordem, sem perdas e sem duplicações.

Mas e quando o TCP não atende aos nossos requisitos? Em cenários modernos, o TCP pode ser considerado "lento" devido ao seu Three-Way Handshake e aos mecanismos de controle de congestionamento rigorosos. Tecnologias modernas, como o QUIC (HTTP/3) criado pelo Google, protocolos de jogos multiplayer (onde a latência é crítica) e protocolos industriais/IoT para dispositivos restritos, constroem suas próprias regras de confiabilidade diretamente sobre o UDP.

O Desafio:

Nesta prática, desceremos ao nível de transporte do UDP. Você assumirá o papel de um engenheiro de redes e criará o seu próprio protocolo de transferência de arquivos.

Seu objetivo é criar um script Cliente (Emissor) e um Servidor (Receptor) capazes de transferir um arquivo (uma imagem ou PDF) de forma íntegra usando apenas sockets UDP. Como o UDP não garante entrega, você terá que programar a lógica de empacotamento, confirmação de recebimento (ACK), retransmissão por estourar o tempo (timeout) e controle da transação.


2. Conceitos Abordados
Sockets UDP (SOCK_DGRAM)
Manipulação de bytes e serialização
Endianness (Big-Endian vs Little-Endian)
Confirmação de recebimento (ACK - Acknowledge)
Mecanismos de Temporização e Retransmissão (ARQ Stop-and-Wait)
Gestão de arquivos no Sistema Operacional (I/O)

3. Pré-requisitos e Links Úteis
Python 3.x instalado.
Editor de código (VSCode, PyCharm).
Dois terminais abertos lado a lado para testes locais.
Links Obrigatórios para Leitura (teremos questionário sobre isso):

Python socket - Documentação Oficial
Python struct - Manipulação de dados binários C
Trabalhando com Arquivos em Python (Read/Write)
O que é o protocolo Stop-and-Wait?
‼️A leitura é fundamental. O texto da prática não terá algumas explicações visto que já constam na documentação oficial.

4. Pesquisa Inicial
Antes de codificar, responda e entenda as seguintes questões (além de responder nos vídeos, também teremos questionários sobre isso). Elas ajudarão nas decisões de design do seu protocolo.

❓ Pesquisa 4.1: Qual é o tamanho máximo seguro que um pacote UDP pode ter para transitar pela internet (ou seja, fora de rede local) sem sofrer fragmentação? Por que isso é necessário? Como isso afeta o tamanho dos pedaços do arquivo que você vai ler por vez no seu código?

❓ Pesquisa 4.2: O que é o conceito de Stop-and-Wait? Desenhe um diagrama de sequência de como o cliente e o servidor conversam nesse modelo se um pacote for perdido.

❓ Pesquisa 4.3: Em redes de computadores, qual é a ordem de bytes padrão para transmissão na rede (Network Byte Order)? É Big-Endian ou Little-Endian?

5. A Biblioteca struct e Endianness
Uma das formas usadas para transferir arquivos através de uma rede consiste em transformar o arquivo numa string. Depois disso, basta enviar essa string como se fosse uma mensagem qualquer de chat. O receptor deve converter a string de modo a obter o arquivo original.

Entretanto, nem sempre esse modo é o mais eficiente.

Para trafegar dados na rede de forma eficiente, não podemos simplesmente converter tudo para String. Um número inteiro 1000 em string ("1000") ocupa 4 bytes (1 byte por caractere). Em formato binário real, ele pode ocupar apenas 2 bytes.

Entretanto a conversão não é tão simples assim. Geralmente temos que usar uma codificação. A codificação mais comum é a base64.

Nesta prática buscaremos usar métodos mais eficientes (realistas e práticos) de codificação para transferência de arquivos. A biblioteca struct do Python permite "empacotar" (pack) e "desempacotar" (unpack) valores do Python em blocos binários (bytes) exatamente como a linguagem C faz.

❓ Pesquisa 5.1: Quais são as situações em que é melhor usar codificação base64 ou usar struct.pack?

Exemplo Prático (Teste no seu terminal interativo do Python):

Código 01 - Serialização e desserialização de dados





Dica: Não salve o arquivo com nome struct.py. Consegue explicar porque?

‼️ Observe como o código realiza as conversões de dados de python para C, como é a ordenação, e como precisamos definir os “campos” de dados explicitamente. Se você lembrar dos pacotes do modelo OSI, estamos começando a chegar num modelo de pacote no qual o emissor e o receptor precisam saber exatamente os dados que estão enviando e recebendo para fazer as conversões corretas.

Nesta prática, usaremos exaustivamente o método pack para montar o cabeçalho antes de anexar o "pedaço" do arquivo a ser enviado.

O cabeçalho do nosso pacote conterá as informações sobre os dados que estão sendo trafegados.

6. Especificação do Nosso Protocolo
Ao criar um protocolo, o engenheiro de redes deve definir como os bits são organizados. O nosso protocolo de transferência será chamado de SRTP (Simple Reliable Transfer Protocol) e terá a seguinte estrutura de pacotes:

Formato do Pacote de Dados (Cliente -> Servidor)

CAMPO

TAMANHO

TIPO (struct)

DESCRIÇÃO

Seq Num

4 bytes

I (unsigned int)

Número de sequência do pacote (0, 1, 2, 3...)

Trans ID

4 bytes

I (unsigned int)

ID único para a transferência (ex: um número aleatório)

Flag

1 byte

B (unsigned char)

0 para dados normais, 1 para o ÚLTIMO pacote do arquivo

Payload

Variável

N/A

Os bytes do arquivo lidos do disco (Máx 1024 bytes)


O cabeçalho total terá 9 bytes (!IIB). O pacote completo (Cabeçalho + Payload) será enviado pelo socket UDP.

Formato do Pacote de Confirmação - ACK (Servidor -> Cliente)

Campo

Tamanho

Tipo (struct)

Descrição

ACK Num

4 bytes

I (unsigned int)

Confirma o recebimento do Seq Num correspondente


7. Implementando o Servidor (Receptor)
Vamos começar construindo o lado que vai receber o arquivo. Crie um arquivo chamado receptor.py.

Passo 1: Configuração do Socket UDP

Inicie o socket UDP e o vincule (bind) à porta local. Essa parte nós já dominados muito bem. Aqui, trago apenas um lembrete.

Código 02 - Socket UDP






Passo 2: O Loop de Recebimento

O servidor precisa de um arquivo de saída onde irá gravar os pedaços recebidos. Além disso, precisamos rastrear qual pacote estamos esperando para evitar pacotes duplicados.

Código 03 - Recepção de dados






8. Implementando o Cliente (Emissor)
Crie o arquivo emissor.py. O cliente lerá um arquivo do disco e usará o protocolo Stop-and-Wait: envia um pacote e espera o ACK. Se ack demorar demais para retornar (timeout), retransmite.

Passo 1: Estrutura Básica

Código 04 - Envio de dados







Passo 2: Lendo o Arquivo e Transmitindo

Abaixo, a estrutura do loop de leitura e transmissão.

Código 05 - Leitura e envio de arquivos



           


9. Controle de Transação e Simulador de Redes Ruins
Se testarmos o código acima localmente (127.0.0.1), ele será tão rápido e perfeito que não veremos o timeout acontecer.

Agora vamos fazer algumas “experimentos” que vão testar nossos conhecimentos. Além disso, poderemos usar esse tipo de experimento para testar situações que podem acontecer no mundo real, mas que não temos controle de como podem acontecer.

‼️Experimentos como esses são usados como parte das técnicas de testes de software, especialmente testes de integração ou testes de sistema. Vocês estudarão testes de software com mais profundidade em outras disciplinas.

👩‍💻 Tarefa A: Controle de Transação (Rollback)

No código do Servidor, você deve adicionar uma lógica:

Se o servidor ficar aguardando o próximo pacote por mais de 10 segundos (sugerindo que o cliente morreu ou desistiu após as 5 tentativas), o servidor deve abortar a transação.

O Requisito: Se a transferência falhar pela metade, o servidor DEVE apagar o arquivo incompleto (recebido.pdf) do disco usando a biblioteca os (pesquise os.remove()). Arquivos corrompidos não devem ficar armazenados.

👩‍💻Tarefa B: Simulador de Perdas de Pacote (Para testar o Retry)

Para provar que seu protocolo de confiabilidade funciona, vamos introduzir o caos.

No Servidor, crie uma função "encapsuladora" para o sock.recvfrom ou simplesmente insira este bloco logo no início do loop principal:


Código 06 - Simulação de rede ruim






Coloque essa simulação de perda tanto na chegada de dados (no Servidor) quanto na recepção de ACKs (no Cliente).
Você verá o seu protocolo brilhando na tela do terminal, exibindo mensagens de Timeout e recuperando os dados perdidos!
10. Questões para Análise
A equipe deve responder a essas perguntas no vídeo. Além disso, deve enviar as respostas no campo de texto do AVA.

Ao transferir um PDF grande rodando localmente sem a "simulação de perda", o arquivo chega íntegro. No entanto, o protocolo Stop-and-Wait é notório por ser ineficiente. Qual a taxa de transferência efetiva que você notou?
Para testar a taxa de transferência do arquivo crie uma variável que conta o tempo de transferência do arquivo. Inicie a variável logo antes do início das transferências e calcule o tempo decorrigo logo após o final da transferência do arquivo. Use qualquer função para pegar o tamanho do arquivo e referencialmente use time.perf_counter() para contar o tempo. Depois basta dividir o tamanho do arquivo pelo tempo calculado. Use as unidades de tempo e tamanho para obter um valor em Mbps. Como “experimento” faça algumas transferências com arquivos muito grandes (> 100 MB ex.: video) ou muito pequenos ( < 1 MB ex.: arquivo de texto) e veja como a taxa de transferência pode variar.
Por que precisávamos lidar com "pacotes duplicados" no servidor se o TCP nunca repete pacotes para a camada de aplicação? Explique uma situação hipotética no qual o cliente reenviaria o pacote SeqNum=5, mesmo após o servidor já tê-lo salvo no disco.
Se você precisasse melhorar a velocidade deste protocolo sem usar TCP, qual técnica substituiria o "Stop-and-Wait"? Pesquise e explique brevemente como funciona uma Janela Deslizante (Sliding Window).
11. Formato de Entrega
Para aprovação nesta prática, você deverá submeter:

Uma pasta compactada com seus códigos-fonte (cliente.py e servidor.py) contendo comentários do que você alterou e das tarefas implementadas. Remova todos os comentários originais e adicione apenas os comentários explicando suas alterações.
O arquivo de texto com as respostas da "Seção 0" e das "Questões para Análise".
Vídeo de Entrega (Máximo 7 minutos) deve conter
Respostas sucintas para todas as questões marcadas com ❓
Explicação do código apenas da modularização, da lógica de Retry e do Controle de Transação (remoção do arquivo corrompido).
Realize a transferência de uma imagem (ex: foto.jpg). Ao final da transferência, abra o arquivo no lado do servidor para provar que a imagem não está corrompida.
Durante o vídeo, a simulação de perda de rede (os 30% de perda sugeridos na Seção 5) DEVE estar ligada. No vídeo, os monitores devem ver claramente os alertas de "Timeout" e "Retransmissão" aparecendo no terminal do emissor, comprovando que seu controle de erros sobre UDP funciona perfeitamente.
No final do vídeo, feche abruptamente o cliente no meio da transferência (usando Ctrl+C ou mesmo fechando o terminal). Mostre o terminal do servidor aguardando e, após 10 segundos, exibindo a mensagem de que apagou o arquivo incompleto do disco. Mostre a pasta provando que o arquivo parcial foi removido.

