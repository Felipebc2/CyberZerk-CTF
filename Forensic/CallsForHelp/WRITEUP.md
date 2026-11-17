<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Calls+for+help" alt="Typing SVG" /></a>

</div>

# Calls for help — FORENSIC · 🟢 INTRO

- **Status:** ✅ RESOLVIDO — mensagem de adeus lida no corpo de um POST HTTP em texto claro
- **Pontos:** 100
- **Anexo / Alvo:** `appels_a_l_aide.pcap` (pcap Ethernet, 12 pacotes, 1 465 bytes, SHA256 `f46758c21328395172b8bc6c969c61934e51621bf257aa8dc2004e1650d05301`)
- **Enunciado:** *"A SOC analyst from Tricatel abruptly resigned yesterday. Before returning its hardware, the network team noticed a final suspicious request coming out of its workstation to an unidentified server. Nous avons récupéré une capture de son trafic réseau local. Analysez cette capture pour retrouver son message d'adieu."*
- **Flag:** `CyberZerk{Exf1ltr4t10n_HTTP_D3s3sp01r}`

---

## TL;DR

1. Captura minúscula de tráfego local (`127.0.0.1`): uma única conexão TCP para a porta 9999.
2. O pacote 6 é um `POST /adieu.php` (`application/x-www-form-urlencoded`) — HTTP sem TLS, conteúdo em texto claro.
3. *Follow TCP Stream* no stream 1 remonta o corpo do formulário; o campo `message` contém a flag.

## Análise

### 1. Visão geral da captura

```bash
capinfos appels_a_l_aide.pcap   # 12 pacotes, 65 s, encapsulamento Ethernet
tshark -r appels_a_l_aide.pcap  # uma linha por pacote
```

| Pacotes | O que acontece |
|---|---|
| 1–2 | `SYN` para `[::1]:9999` → `RST, ACK`: nada escutando em IPv6. Típico de cliente (ex.: `curl localhost`) que tenta `::1` primeiro e cai para IPv4 |
| 3–5 | *3-way handshake* TCP `127.0.0.1:52058 → 127.0.0.1:9999` (`SYN` → `SYN, ACK` → `ACK`) |
| **6** | **`POST /adieu.php HTTP/1.1 (application/x-www-form-urlencoded)`** — a requisição suspeita |
| 7–12 | Só `ACK`, um *keep-alive* (~63 s depois) e o encerramento `FIN`. **Nenhuma resposta HTTP**: do outro lado havia apenas um *listener* cru (estilo `nc -l 9999`), não um servidor web |

Hipótese: a "mensagem de adeus" está no **corpo** do POST (em `POST` os dados vão no corpo, não na URL).

### 2. Remontagem da conversa (Follow TCP Stream)

O tshark numera cada conexão em `tcp.stream`: a tentativa IPv6 (pacotes 1–2) é o stream **0**; a conexão IPv4 é o stream **1**.

```bash
tshark -r appels_a_l_aide.pcap -qz follow,tcp,ascii,1
```

```http
POST /adieu.php HTTP/1.1
Host: localhost:9999
Accept: */*
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) BurnoutBrowser/1.0
Content-Type: application/x-www-form-urlencoded
Content-Length: 198

employe=Marc_V&statut=epuisement_total&message=Je quitte Tricatel. Le management me d..truit la sant.. mentale. Je n'ai plus dormi depuis 3 jours. Adieu. Flag: CyberZerk{Exf1ltr4t10n_HTTP_D3s3sp01r}
```

Leitura:

- **Corpo** = três campos de formulário separados por `&`: `employe=Marc_V`, `statut=epuisement_total`, `message=...`.
- Os `..` em `d..truit` / `sant..` não são codificação: são o `é` em UTF-8 (2 bytes, `0xC3 0xA9`), que o modo `ascii` do tshark exibe como `.` por estar fora do ASCII. Texto original: *"détruit"*, *"santé"* (`follow,tcp,hex,1` mostra os bytes).
- `User-Agent: BurnoutBrowser/1.0` é a assinatura do autor do challenge.
- Lição: **HTTP sem TLS = texto claro**. Qualquer um no caminho (ou com uma captura local) lê a exfiltração inteira.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Corpo URL-encoded (`%7B`, `+`...) exigiria decodificação | ✗ (falsificada) | Apesar do `Content-Type`, o cliente mandou o corpo cru (espaços literais, `{}` sem `%`); bastou ler |
| Seguir o stream TCP 0 | ✗ | Stream 0 é a tentativa IPv6 recusada (`SYN`/`RST`), sem payload; a conversa está no stream 1 |
| Resposta do servidor teria algo | ✗ | Não existe resposta HTTP: só `ACK`/`FIN` vindos da porta 9999 |

## Conclusão

Challenge introdutório de forense de rede: visão geral (`capinfos`/`tshark -r`) → identificar o pacote de aplicação relevante → *Follow TCP Stream* para remontar o payload. A flag estava em texto claro no campo `message` do formulário enviado a `/adieu.php`.

---

## Apêndice — ferramentas

- `capinfos appels_a_l_aide.pcap` — metadados da captura (nº de pacotes, duração, hashes).
- `tshark -r appels_a_l_aide.pcap` — lista de pacotes (equivale ao painel superior do Wireshark).
- `tshark -r appels_a_l_aide.pcap -T fields -e frame.number -e tcp.stream` — mapeia pacote → índice de stream.
- `tshark -r appels_a_l_aide.pcap -qz follow,tcp,ascii,1` — remonta o stream TCP 1 (Wireshark: botão direito → *Follow → TCP Stream*).
