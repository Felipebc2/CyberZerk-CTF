<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Restructuring" alt="Typing SVG" /></a>

</div>

# Restructuring — WEB · 🔴 DIFÍCIL

- **Status:** ✅ RESOLVIDO — SSRF no preview do Tricatel → loopback que escapa da denylist + porta interna real → `interne.php` libera.
- **Pontos:** 175 (dinâmico) · author Perceval
- **Alvo:** `restructuration.cyberzerk.fr`
- **Enunciado:** *"Tricatel's 'report preview generator' will search for the contents of a URL for you. An internal HR vault (interne.php) is only supposed to be reachable from the application network. Make the waiter speak for you."*
- **Flag:** `CyberZerk{SSRF_V3rs_L3_C0ffr3_Int3rn3}`

---

## TL;DR

1. O "Tricatel — report preview generator" recebe `?url=` e **o servidor busca o conteúdo** pra você → **SSRF**. "Make the waiter speak for you" = usar o garçom (servidor) como proxy pra alcançar o que você não alcança.
2. O cofre `interne.php` decide por **IP de origem** (`REMOTE_ADDR`): de fora, a borda aparece como `172.23.0.3` e leva `403 — Réservé au réseau interne`.
3. Payload vencedor: **`http://127.0.0.2:8080/interne.php`** — três camadas resolvidas de uma vez (loopback que escapa da denylist + porta interna real atrás do proxy + esquema permitido).

## Análise

### 1. Vetor: SSRF confirmado

`GET /?url=<URL>` e o *preview* mostra o que o **servidor** buscou. Quem faz a requisição HTTP é o backend, não o browser — SSRF clássico.

### 2. O alvo interno

`https://restructuration.cyberzerk.fr/interne.php` direto no browser:

```
403 - Réservé au réseau interne (votre IP : 172.23.0.3)
```

O cofre decide por `REMOTE_ADDR`, e o pedido externo chega nele através de um **proxy reverso** que aparece como `172.23.0.3` (rede Docker `172.23.0.0/16`) — não está na allowlist. Quem **está** na allowlist é a própria aplicação (loopback / rede interna).

### 3. Lendo o filtro (oráculo de 3 estados)

Interrogar o gerador com entradas escolhidas separa as respostas em três mensagens — e **cada mensagem é um sinal**:

| Resposta | Significa |
|---|---|
| `Hôte interne interdit par la politique de sécurité` | o filtro **reconheceu** o host como proibido |
| `Impossible de récupérer cette URL` | passou pelo filtro, mas a busca não deu 200 (sem rota / porta fechada / formato recusado) |
| `Schéma non autorisé (http/https uniquement)` | esquema fora de http/https |

Com isso, caracterizamos cada defesa:

| Entrada | Resposta | Conclusão |
|---|---|---|
| `127.0.0.1`, `127.0.0.1.`, `[::ffff:127.0.0.1]`, `localhost`, `LOCALHOST` | `interdit` | **denylist de substring** `127.0.0.1` + nome `localhost` (case-insensitive) |
| `127.1`, `2130706433`, `127.000.000.001`, `127.0.0.2` | `Impossible` | **passam** a denylist (string não contém `127.0.0.1`) |
| `file:///etc/passwd` | `Schéma non autorisé` | **só http/https** (sem `file://`) |

A denylist **não resolve DNS** — é match de texto: `[::ffff:7f00:1]` (127.0.0.1 em hex) passou, enquanto `[::ffff:127.0.0.1]` (dígitos visíveis) foi bloqueado.

### 4. Sem egress externo

Servidor local de redirect (`redir.py`) + túnel `localhost.run`, apontando o gerador pra ele: **zero** hits no nosso log (só o nosso próprio browser). `http://1.1.1.1/` → `Impossible`. Logo, o garçom **não fala com a internet** → mata redirect-bypass e DNS rebinding, e confirma que `Impossible` = "não conectou / não deu 200", não bloqueio sofisticado.

### 5. O pulo do gato: a porta

Com loopback escapando da denylist (`127.0.0.2`) e sem egress, faltava **por que `http://127.0.0.2/interne.php` (porta 80) dava `Impossible`**. Resposta: a **:80 externa é do proxy reverso** (`172.23.0.3`); o serviço real (Apache) atrás dele escuta em **:8080**. Toda a varredura anterior tinha sido na :80 — a aplicação respondia noutra porta.

### 6. Combo vencedor

```
http:// │ 127.0.0.2 │ :8080 │ /interne.php
  │          │          │          └─ o cofre
  │          │          └─ porta interna real (atrás do proxy :80)
  │          └─ loopback (127.0.0.0/8) que escapa da denylist de string
  └─ esquema permitido (file:// era bloqueado)
```

O servidor conectou em `127.0.0.2:8080` (ele mesmo), o `interne.php` viu origem de **loopback = rede interna** → liberou o cofre, flag incluída:

```
CyberZerk{SSRF_V3rs_L3_C0ffr3_Int3rn3}
```

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| XSS refletido | ✗ | o "preview" é renderizado no **servidor**; não há vítima client-side. É SSRF. |
| `localhost` / `127.0.0.1` / `[::ffff:127.0.0.1]` / `LOCALHOST` | ✗ | `interdit` — denylist de substring + nome |
| Redirect via webhook.site / servidor próprio + túnel | ✗ | **sem egress** — o garçom nunca alcança o redirecionador |
| `file://`, `file:///etc/hosts` | ✗ | `Schéma non autorisé` — só http/https |
| `127.0.0.2/interne.php` **na porta 80** | ✗ | :80 é do proxy; o app real estava na :8080 (o erro foi **não variar a porta**) |
| Varredura `172.23.0.{1..17}` (porta 80) | ✗ | `Impossible` — mesma armadilha da porta / origem errada |

> **Lição metodológica:** o gargalo não foi um payload exótico, foi **assumir a porta :80**. Minha análise parcial chegou a concluir que "o loopback estava selado" — estava errada: faltava variar a porta. Ler `interdit` vs `Impossible` como sinais distintos foi o que separou "filtro" de "não conectou", mas só fechou quando o `:8080` entrou.

## Conclusão

SSRF onde o fetcher server-side alcança o loopback da própria aplicação. A denylist de string (`127.0.0.1`/`localhost`) é trivialmente burlável porque **todo o `127.0.0.0/8` é a máquina local** — `127.0.0.2` resolve pro mesmo host sem conter a substring proibida. Somado a isso, o serviço real atrás do proxy numa porta não-padrão (`:8080`) escondia o alvo de uma varredura ingênua da :80.

### Mitigação

- Não filtrar SSRF por **denylist de string**: normalizar e resolver o host, bloqueando **todo** `127.0.0.0/8`, `::1`, `169.254.0.0/16`, ranges RFC1918 e o próprio hostname — por IP resolvido, não por texto.
- Validar também **porta** (allowlist de destinos), não só host.
- Idealmente, não deixar o serviço buscar URLs arbitrárias: allowlist de domínios, egress bloqueado (que aqui ajudou, mas não bastou contra loopback).
- O cofre não deveria confiar cegamente em `REMOTE_ADDR` de loopback para liberar segredo — autenticação real entre serviços.

---

## Apêndice — ferramentas

- `solve.sh` — `bash solve.sh '<cf_clearance>'`: itera payloads de bypass de loopback contra `?url=`, classificando ao vivo cada resposta (`interdit` / `Impossible` / corpo / flag).
- `sweep.sh` — `bash sweep.sh '<cf_clearance>'`: varre `172.23.0.0/24` via SSRF com oráculo de **timing**; útil, mas o alvo estava no próprio loopback numa **porta** não varrida.
- `redir.py` — servidor de redirect local + log de hits (IP/User-Agent), usado com `ssh -R 80:localhost:8000 localhost.run` para provar (negativamente) o egress.

### Payload final

```text
http://127.0.0.2:8080/interne.php
```
