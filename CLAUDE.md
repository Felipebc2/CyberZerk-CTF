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

`<Categoria>/<NomeDoChallenge>/` com `README.md` (card) + `WRITEUP.md` (segue `WRITEUP_TEMPLATE.md`) + artefatos/solve. Pastas: `Web`, `Awareness`, `Steganography`, `Cryptography`, `Forensic`, `Miscellaneous` (inclui os retos de Warm-up e Signature da plataforma). Nome da pasta do reto em PascalCase sem acento (ex.: `Miscellaneous/SignatureReglement`). Prints em `img/`. Ao mudar status de um reto, atualizar a tabela do `README.md` raiz. Artefatos >100 MB vão para o `.gitignore` (sha256 no writeup).

## Regras invioláveis

1. NUNCA executar nada contra alvo do reto, plataforma ou infra (curl, nc, nmap, ssh, requests, browser...). Quem roda é o usuário.
2. Escopo = só os subdomínios/IPs explicitamente dados em cada reto. Nada na infra da Hyperion Cloud, Cloudflare ou terceiros.
3. Proibido: DoS, scan massivo, contornar proteções da plataforma. Falha na plataforma → reportar em `ctf@cyberzerk.fr`, não explorar.
4. Nunca enviar flags, nunca compartilhar flag/solução fora deste repo.
5. Repo privado; push/publicação só a pedido do usuário.
6. Só máquina e rede pessoais (nada de PC/VPN/rede de empregador). Arquivos do reto (binários, malware) analisar em VM/container.

## Writeups

`WRITEUP.md` por reto seguindo `WRITEUP_TEMPLATE.md`, em português, e tabela do `README.md` atualizada junto. Anonimizar credenciais reais e hosts de infra (`<HOST>`, `<USER>`, `<TOKEN>`); flags e valores derivados do reto ficam.
