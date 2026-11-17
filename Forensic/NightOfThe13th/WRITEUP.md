<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Night+of+the+13th" alt="Typing SVG" /></a>

</div>

# Night of the 13th — FORENSIC · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — requisição de exfiltração isolada no access log; flag no parâmetro `token`, URL-encoded
- **Pontos:** 75
- **Anexo / Alvo:** `access.log` (log de acesso no formato Combined, 121 linhas, 12,7 KB, SHA256 `b28a3d6e06eff5d1e9ac286637ec88b65b93db6efb2b505dc27b7ce9d35ef507`)
- **Enunciado:** *"On the night of November 13, a confidential file left the Tricatel intranet. Here is the server access log. Find the successful exfiltration request."*
- **Flag:** `CyberZerk{L0g_4n4lys3_Exf1l_C0nf1rm33}`

---

## TL;DR

1. O log tem 121 requisições entre 02:00:00 e 02:47:03. Todas vêm da rede interna `10.0.0.0/24`, exceto **uma**: `45.83.12.207`.
2. Essa requisição é a única para `/export.php`. Ela pede `rapport_confidentiel_rh.zip`, recebe `200` e transfere **184 320 bytes**, cerca de 46 vezes a maior resposta legítima.
3. O parâmetro `token` está URL-encoded. Trocando `%7B` por `{` e `%7D` por `}`, sai a flag.

## Análise

### 1. Anatomia de uma linha (Combined Log Format)

```
45.83.12.207 - - [13/Nov/2026:02:47:03 +0100] "GET /export.php?file=...&token=... HTTP/1.1" 200 184320 "-" "curl/8.2.1"
│            │ │  │                            │                                             │   │      │   └ User-Agent
│            │ │  │                            │                                             │   │      └ Referer
│            │ │  │                            │                                             │   └ bytes enviados na resposta
│            │ │  │                            │                                             └ status HTTP
│            │ │  │                            └ linha da requisição (método, URL com query string, protocolo)
│            │ │  └ data/hora (fuso de Paris, +0100)
│            │ └ usuário autenticado (vazio)
│            └ ident (vazio)
└ IP do cliente
```

Com `awk`, cada campo vira uma coluna separada por espaço: `$1` é o IP, `$7` é a URL, `$9` é o status e `$10` são os bytes. É isso que permite contar e ordenar cada um.

### 2. Triagem: o que destoa do ruído?

"Exfiltração bem-sucedida" se traduz em três critérios: **quem** pede (de fora da empresa), **o quê** (um recurso incomum) e **se funcionou** (status `200` com muitos bytes transferidos).

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn   # IPs: só 10.0.0.x... e 1 outlier
grep -v '^10\.' access.log                                # tudo que NÃO é rede interna
awk '{print $7}' access.log | cut -d? -f1 | sort | uniq -c | sort -rn   # endpoints
awk '{print $10}' access.log | sort -n | tail -3          # maiores respostas
```

| Critério | Tráfego normal | Requisição suspeita (linha 94) |
|---|---|---|
| IP de origem | `10.0.0.x` (rede interna, 120 linhas) | **`45.83.12.207`** (externo, único) |
| Endpoint | `/`, `/login`, `/rh/dossier`, `/api/absences`, `/intranet`, estáticos | **`/export.php`** (1 ocorrência) |
| Recurso | páginas da intranet | **`file=rapport_confidentiel_rh.zip`** |
| Status | mistura de 200 / 304 / 404 / 302 | **`200`**, ou seja, o download funcionou |
| Bytes | no máximo 3 959 | **184 320** (cerca de 180 KB, o tamanho de um zip) |
| Horário | 02:00 → 02:46 | 02:47:03, a última requisição da noite |

Todos os critérios apontam para a mesma linha:

```
94:45.83.12.207 - - [13/Nov/2026:02:47:03 +0100] "GET /export.php?file=rapport_confidentiel_rh.zip&token=CyberZerk%7BL0g_4n4lys3_Exf1l_C0nf1rm33%7D HTTP/1.1" 200 184320 "-" "curl/8.2.1"
```

**Ligação com outro challenge:** `45.83.12.207` é o mesmo IP do relay `mail-cheap-relay.ru` que enviou o e-mail falso do DRH em [HR email](../HREmail/WRITEUP.md). É o mesmo ator nos dois challenges.

### 3. Montar a flag (URL-decode)

URLs só podem conter alguns caracteres ASCII. O resto é codificado como `%` seguido do byte em hexadecimal (*percent-encoding*, RFC 3986):

| Codificado | Hex | Caractere |
|---|---|---|
| `%7B` | 0x7B | `{` |
| `%7D` | 0x7D | `}` |

```
CyberZerk%7BL0g_4n4lys3_Exf1l_C0nf1rm33%7D  →  CyberZerk{L0g_4n4lys3_Exf1l_C0nf1rm33}
```

Para fazer o mesmo pela CLI: `python3 -c "import urllib.parse as u; print(u.unquote('CyberZerk%7BL0g_4n4lys3_Exf1l_C0nf1rm33%7D'))"`. No CyberChef, use a receita *URL Decode*.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Filtrar pelo User-Agent `curl/` | ✗ (ruído) | 42 das 121 linhas usam `curl/8.2.1`, inclusive de IPs internos. O UA não separa nada |
| Ler o log em ordem como linha do tempo | ✗ (enganoso) | As linhas não estão em ordem cronológica: a última linha do arquivo é de 02:33. Para ordenar, use o campo de data (`$4`), não a posição da linha |

## Conclusão

Challenge de triagem de log: em vez de ler 121 linhas, conta-se cada campo (`uniq -c`) e procura-se o *outlier*. Um único IP externo, um endpoint usado uma só vez, o nome do arquivo confidencial e uma resposta `200` de 180 KB identificam a exfiltração. Por fim, o `token` URL-encoded dá a flag.

---

## Apêndice — ferramentas

- `awk '{print $N}' access.log | sort | uniq -c | sort -rn`: histograma de qualquer campo (IP, URL, status, UA).
- `grep -v '^10\.' access.log`: isola o tráfego que não vem da rede interna.
- `awk '{print $10}' access.log | sort -n | tail`: maiores respostas, onde aparece um possível vazamento de volume.
- `python3 -c "import urllib.parse as u; print(u.unquote('...'))"` ou CyberChef *URL Decode*: percent-decoding.
