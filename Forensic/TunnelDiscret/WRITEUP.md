<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Tunnel+Discret" alt="Typing SVG" /></a>

</div>

# Tunnel Discret — FORENSIC · 🔴 DIFFICULT

- **Status:** ✅ RESOLVIDO — exfiltração por DNS: a flag sai em hex, 6 bytes por consulta, nos subdomínios de `exfil-4167c682.tricatel-interne.fr`
- **Pontos:** 175
- **Anexo / Alvo:** `capture.pcap` (1 681 bytes, 14 pacotes, SHA256 `b3c433e558277c8b19508b05974146e50631bfa3b4b88d1c18c285438317dee6`) + `README.txt`
- **Enunciado:** *"Capture réseau d'un poste. Un processus parle beaucoup au DNS. Que fait-il sortir ?"* (no README.txt: *"Capture réseau d'un poste Tricatel. Un processus semble 'parler' beaucoup au DNS. Que fait-il sortir ?"*)
- **Flag:** `CyberZerk{dns_3xf1ltr4t10n_r34ss3mbl3_l3s_s0us_d0m41n3s}`

---

## TL;DR

1. O pcap só tem consultas DNS do tipo `A`, todas de `10.10.0.57` para o resolver `10.10.0.1`.
2. Dez delas seguem o padrão `NN.<hex>.exfil-4167c682.tricatel-interne.fr`: um número de sequência, um bloco de dados em hex e um ID de sessão.
3. Ordenando pela sequência, juntando os blocos hex e decodificando, sai a flag.

## Análise

### 1. Triagem do pcap

```bash
tshark -r capture.pcap
tshark -r capture.pcap -q -z io,phs   # hierarquia de protocolos
```

São 14 pacotes, todos `eth / ip / udp / dns` para a porta 53, e todos são **consultas sem resposta**. O "processus qui parle beaucoup au DNS" do enunciado é a máquina `10.10.0.57`.

### 2. Só os nomes consultados

```bash
tshark -r capture.pcap -T fields -e dns.qry.name
```

`-T fields -e <campo>` faz o tshark imprimir só os campos pedidos, e não o resumo do pacote:

```
00.43796265725a.exfil-4167c682.tricatel-interne.fr
01.65726b7b646e.exfil-4167c682.tricatel-interne.fr
...
09.737d.exfil-4167c682.tricatel-interne.fr
intranet.tricatel-interne.fr
mail.tricatel-interne.fr
wiki.tricatel-interne.fr
proxy.tricatel-interne.fr
```

As 4 últimas são nomes normais da rede interna, puro ruído. As 10 primeiras têm uma estrutura clara:

| Label | Exemplo | Papel |
|---|---|---|
| 1º | `00` … `09` | número de sequência, para remontar na ordem |
| 2º | `43796265725a` | 12 caracteres hex = 6 bytes de dado (o último bloco, `737d`, tem 2) |
| 3º | `exfil-4167c682` | ID da sessão de exfiltração |
| resto | `tricatel-interne.fr` | domínio |

Nessas 10 consultas o *transaction ID* do DNS (`dns.id`) também vai de `0x0000` a `0x0009`, repetindo a sequência. Nas 4 consultas normais ele fica em `0x0000`.

### 3. Por que o DNS serve para vazar dados

Firewalls costumam bloquear conexões diretas para fora, mas deixam o DNS passar, porque sem ele nada funciona. Quem responde uma consulta é o **servidor autoritativo do domínio**. Se o atacante controla a zona `exfil-…`, qualquer consulta a `ALGUMA_COISA.exfil-…` atravessa o resolver interno e chega ao servidor dele, levando o dado **dentro do próprio nome consultado**. Ele nem precisa responder.

As regras do DNS explicam o formato:

- cada label tem no máximo 63 caracteres, e o nome inteiro no máximo 253, então o dado é fatiado;
- o DNS não diferencia maiúsculas de minúsculas e só aceita `a-z 0-9 -`, então o dado vai em **hex** (ou base32), não em base64;
- os pacotes UDP podem chegar fora de ordem, então cada fatia leva um número de sequência.

### 4. Remontar

O primeiro bloco já mostra o que é: `43 79 62 65 72 5a` em ASCII é `CyberZ`.

**CyberChef**: cole as 10 linhas `exfil` no Input e monte a receita:

1. **Regular expression**: regex `^\d+\.([0-9a-f]+)\.`, *Output format* **List capture groups** (fica só o bloco hex de cada linha);
2. **From Hex**: *Delimiter* **Auto**.

**Terminal** (o `xxd` não estava instalado, então a conversão final é feita em Python):

```bash
tshark -r capture.pcap -T fields -e dns.qry.name | grep exfil \
  | sort -t. -k1,1n | cut -d. -f2 \
  | python3 -c "import sys; print(bytes.fromhex(sys.stdin.read().replace(chr(10),'')).decode())"
```

| Seq | Hex | Texto |
|---|---|---|
| 00 | `43796265725a` | `CyberZ` |
| 01 | `65726b7b646e` | `erk{dn` |
| 02 | `735f33786631` | `s_3xf1` |
| 03 | `6c7472347431` | `ltr4t1` |
| 04 | `306e5f723334` | `0n_r34` |
| 05 | `7373336d626c` | `ss3mbl` |
| 06 | `335f6c33735f` | `3_l3s_` |
| 07 | `733075735f64` | `s0us_d` |
| 08 | `306d34316e33` | `0m41n3` |
| 09 | `737d` | `s}` |

A flag descreve a técnica: *"DNS exfiltration : réassemble les sous-domaines"*, ou seja, remontar os subdomínios.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Os dados estarem nas **respostas** DNS (registros `A`/`TXT`) | ✗ (falsificada) | Não há nenhuma resposta na captura, só consultas; o dado vai no nome consultado |
| As consultas chegarem fora de ordem e o `sort` ser obrigatório | ✗ (não foi o caso) | Os pacotes já estavam em ordem `00` → `09`; o `sort` fica no comando só para o caso geral |
| As 4 consultas finais (`intranet`, `mail`, `wiki`, `proxy`) carregarem algo | ✗ (ruído) | São nomes internos normais, sem bloco de dado e sem sequência |
| Ferramenta pronta para decodificar | ✗ | Cada malware tem o próprio formato (o `dnscat2`, por exemplo, tem decoder só para o protocolo dele); a remontagem é manual |

## Conclusão

Exfiltração por *DNS tunneling*: o dado é codificado em hex, fatiado em labels de subdomínio, numerado e enviado como consultas para um domínio que o atacante controla. Para recuperar: filtrar as consultas do domínio suspeito, ordenar pela sequência, extrair os blocos e decodificar.

Lição defensiva: o DNS precisa ser monitorado como qualquer outro canal de saída. Sinais de alerta:

- muitas consultas únicas para o mesmo domínio pai;
- labels longos com cara de hex ou base32 (alta entropia);
- números de sequência no nome;
- consultas que nunca recebem resposta.

Para mitigar:

- forçar as estações a usar só o resolver interno, bloqueando a porta 53 de saída e o DoH para fora;
- aplicar RPZ ou listas de bloqueio;
- alertar em volume e entropia por domínio, com Zeek ou um IDS como Suricata.

---

## Apêndice — ferramentas

- `tshark -r X` (resumo) / `tshark -r X -q -z io,phs` (protocolos presentes).
- `tshark -r X -T fields -e dns.qry.name -e dns.id`: extrai só os campos que interessam.
- `tshark -r X -Y 'dns.qry.name contains "exfil"'`: filtro de exibição direto no tshark.
- `sort -t. -k1,1n`, `cut -d. -f2`: ordenar pela sequência e isolar o bloco de dados.
- CyberChef: **Regular expression** (List capture groups) + **From Hex**.
- `bytes.fromhex()` em Python (ou `xxd -r -p`, que vem com o `vim` no Arch).
