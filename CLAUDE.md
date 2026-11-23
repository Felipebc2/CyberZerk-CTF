# CTF CyberZerk 2026

Responda em português. Writeups em português.

- Regulamento: `docs/regulamento.md` (resumo PT-BR; oficial no site; casos omissos = organização)
- Confidencialidade: `docs/confidencialidade.md` (site atrás da Cloudflare, hospedado na Hyperion Cloud: nenhum dos dois é alvo)
- Plataforma: https://ctf.cyberzerk.fr/challenges (único meio de envio). Suporte: `ctf@cyberzerk.fr` ou Discord da associação
- Online, **individual** (uma conta por pessoa). Jeopardy, pontuação dinâmica (cai conforme mais gente resolve)
- Datas (Paris = UTC+1 em novembro; Brasília = Paris − 4h): **09/11 14h → 22/11 18h Paris = 09/11 10h → 22/11 14h Brasília**. Depois disso o placar congela
- Flag: `CyberZerk{...}`. Só sugerir flag confirmada, nunca chutada
- Flags públicas (já enviadas): regulamento `CyberZerk{J_AI_LU_ET_J_ACCEPTE_LE_REGLEMENT_2026}`, confidencialidade `CyberZerk{J_AI_LU_LA_CONFIDENTIALITE_2026}` (Signature, 1 pt cada), warm-up `CyberZerk{BIENVENUE_AU_CTF_CYBERZERK}` (0 pt)
- Troféus com pontos bônus: first blood (exceto intro), desafio difícil, desafio extremo, seção completa

## Credenciais

Em `CLAUDE.local.md` (gitignored). Nunca colocar credenciais em arquivo rastreado.

## Estrutura

`<Categoria>/<NomeDoChallenge>/` com `README.md` (card) + `WRITEUP.md` (segue `WRITEUP_TEMPLATE.md`) + artefatos/solve. Pastas: `Web`, `Awareness`, `Steganography`, `Cryptography`, `Forensic`, `Miscellaneous` (inclui os challenges de Warm-up e Signature da plataforma). Nome da pasta do challenge em PascalCase sem acento (ex.: `Miscellaneous/SignatureReglement`). Prints em `img/`. Ao mudar status de um challenge, atualizar a tabela do `README.md` raiz. Artefatos >100 MB vão para o `.gitignore` (sha256 no writeup).

## Regras invioláveis

1. NUNCA executar nada contra alvo do challenge, plataforma ou infra (curl, nc, nmap, ssh, requests, browser...). Quem roda é o usuário.
2. Escopo de ataque = os subdomínios/IPs dados em cada challenge. Nesses alvos, **aprofundar além da solução pretendida é permitido** sob a seção *Caça a vulnerabilidades* abaixo. Permanecem **fora de escopo, nunca tocar**: infra da Hyperion Cloud, Cloudflare, terceiros, e contas/dados de outros participantes.
3. Sempre proibido: DoS, scan massivo, destruição, persistência, exfiltração de dados de terceiros. Achar falha **além do escopo de um challenge** (RCE no box, acesso à infra/outro challenge/dados) agora é **objetivo premiado** pelo org: parar na fronteira, montar PoC mínimo e **reportar** em `ctf@cyberzerk.fr`/Discord (ver seção abaixo) — nunca explorar além da prova nem weaponizar.
4. Nunca enviar flags, nunca compartilhar flag/solução fora deste repo.
5. Repo privado; push/publicação só a pedido do usuário.
6. Só máquina e rede pessoais (nada de PC/VPN/rede de empregador). Arquivos do challenge (binários, malware) analisar em VM/container.

## Caça a vulnerabilidades e divulgação responsável (bug bounty)

O org **convida e premia** achar falhas que ultrapassam o escopo de um challenge (troféu *Vulnerability Founded*, +500 pts) — **desde que reportadas, não exploradas à toa**. Política:

- **Permitido** nos alvos dados: empurrar o challenge além do pretendido (ex.: virar LFI/SSTI em RCE no próprio box do challenge) para **demonstrar** a falha.
- **Na fronteira, PARE.** No instante em que o acesso ultrapassa o challenge (infra, outro challenge, dados de terceiros, rede interna), **não avance**: capture um **PoC mínimo** (prova de alcance — um `id`, um hostname, um config do *próprio* app), **sem** exfiltrar dados de outros, sem mexer em produção, sem persistência, sem destruir.
- **Reportar** pelo canal oficial (`ctf@cyberzerk.fr` ou Discord) com PoC e passos. Só compartilhar com o org; PoC/relatório ficam no repo privado.
- **Quem executa contra o alvo continua sendo o usuário** (regra nº1): eu desenho o PoC e o relatório, **você** roda e envia.
- **Fora de escopo permanente, nem pra PoC:** Hyperion Cloud, Cloudflare, terceiros, contas/dados de outros participantes, DoS, scan massivo.

> Honestidade: o prêmio é **discricionário** do org e vem *por reportar com responsabilidade*. O caminho mais seguro — e que ainda ganha os pontos — é **demonstrar o mínimo e reportar**; não precisa modificar app ao vivo nem pivotar de verdade pra provar que dá.

## Metodologia de ensino (como trabalhar os challenges comigo)

Estes challenges são para **eu aprender**, não só para resolver. O padrão:

1. **Ensinar passo a passo, um conceito por vez.** Não pular na frente, não despejar a solução inteira de uma vez. A cada passo, parar e checar se entendi antes de avançar.
2. **Explicar a mecânica (o quê e o porquê), não só o comando.** Anatomia da coisa, por que o bug existe, por que o payload funciona — não apenas "cola isto aqui".
3. **Quem executa contra o alvo sou eu.** O fluxo é: você explica → **eu** rodo (curl/browser/script) e reporto o resultado → seguimos. (reforça a regra inviolável nº 1)
4. **Não criar scripts/artefatos por conta própria.** Só escrever script quando eu **pedir explicitamente**. Quando eu pedir, o script deve **imprimir progresso ao vivo** (nada de rodar silencioso) e rodar em **foreground/local**, a menos que eu peça background. Me passar o comando pra eu mesmo rodar.
5. **Raciocínio em playbook, com honestidade.** Formular **hipótese** → **testar interrogando o oráculo** (ler as respostas do alvo a entradas escolhidas) → se a hipótese for **falsificada**, dizer isso claramente e **pivotar**. Hipótese derrubada é **dado, não fracasso**; assumir erros meus de rumo sem enrolar.
6. **Usar o Arsenal do `ctf-dispatch` como playbook.** Se não houver ficha pro vetor, ensinar direto. Obs.: os subagents do dispatch ficam bloqueados pelo hook do context-mode → substituir por **triagem manual + ensino direto** do playbook.

## Writeups

`WRITEUP.md` por challenge seguindo `WRITEUP_TEMPLATE.md`, em português, e tabela do `README.md` atualizada junto. Documentar a **trilha honesta**, incluindo hipóteses que falharam (seção "O que não funcionou"). Anonimizar credenciais reais e hosts de infra (`<HOST>`, `<USER>`, `<TOKEN>`); flags e valores derivados do challenge ficam.
