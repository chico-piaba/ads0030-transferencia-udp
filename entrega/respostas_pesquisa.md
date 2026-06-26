# Respostas das perguntas de pesquisa — ADS0030

> Preencha/ajuste com suas palavras antes de entregar. As respostas abaixo
> são um ponto de partida correto e completo.

---

## Pesquisa 8.1 — "Será possível testar através da internet? Explique."

**Resposta curta:** Sim, é possível, mas exige configuração extra. Não funciona
"de graça" como no `127.0.0.1`.

**Por quê (explicação):**

1. **IP público e NAT.** Em casa, seu roteador usa NAT: vários dispositivos
   compartilham **um único IP público**. O cliente externo não enxerga o IP
   privado (`192.168.x.x` / `127.0.0.1`) da máquina do servidor. É preciso usar
   o **IP público** do roteador.

2. **Port forwarding (redirecionamento de porta).** Como o roteador não sabe
   para qual máquina interna entregar o pacote UDP que chegou na porta 8080, você
   precisa criar uma regra no roteador: "tudo que chegar em UDP:8080 → manda para
   o IP interno da máquina do servidor".

3. **Firewall.** O firewall do sistema operacional (e às vezes do provedor) pode
   bloquear UDP na porta 8080. É preciso liberar.

4. **UDP é "sem conexão".** Muitos provedores e firewalls tratam UDP de entrada
   com desconfiança (usado em ataques/DDoS), então é comum ele ser filtrado.

5. **Perda real e fragmentação (MTU).** Pela internet, a perda de pacotes é real
   (não só simulada) e pacotes maiores que o **MTU** (~1500 bytes) podem ser
   fragmentados ou descartados. Por isso o payload de **1024 bytes** é uma escolha
   segura — cabe folgadamente dentro do MTU junto com os 9 bytes de cabeçalho.

**Conclusão:** Para testar pela internet, use o IP público + port forwarding +
liberação no firewall. Em ambiente acadêmico, o caminho mais simples é testar
entre duas máquinas na **mesma rede local (LAN)** ou usando uma **VM/contêiner**,
como o próprio enunciado sugere.

---

## (Demais perguntas "Pesquisa X.Y" do enunciado)

> O `contexto.md` veio vazio, então só a Pesquisa 8.1 aparece nas imagens.
> Cole aqui as outras perguntas que estiverem no PDF do enunciado que eu completo.

- **Pesquisa __.__ —** ...
- **Pesquisa __.__ —** ...

---

## Perguntas conceituais que costumam cair (bônus de estudo)

- **Por que UDP e não TCP?** Para *aprender* a construir confiabilidade na mão.
  O TCP já faz tudo isso (ordenação, retransmissão, controle de fluxo); o
  exercício é simular isso sobre o UDP, que é "cru".
- **O que é o cabeçalho `!IIB`?** `!` = ordem de bytes da rede (Big-Endian),
  `I` = inteiro sem sinal de 4 bytes, `B` = byte sem sinal. Total = 9 bytes.
- **Para que serve o `trans_id`?** Identifica uma transferência específica. Se
  dois clientes mandarem ao mesmo tempo, o servidor ignora os "pacotes
  alienígenas" de outra transação.
- **O que é Stop-and-Wait?** Envia 1 pacote e só envia o próximo depois de receber
  o ACK. Simples, porém lento (espera 1 RTT por pacote).
- **O que acontece se o ACK se perde (e não o pacote)?** O cliente retransmite, o
  servidor recebe um pacote duplicado, percebe que `seq_num != seq_esperado` e
  **reenvia o ACK** sem gravar de novo — evitando arquivo corrompido.
