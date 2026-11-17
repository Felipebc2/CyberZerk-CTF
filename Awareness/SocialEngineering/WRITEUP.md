<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Social+Engineering" alt="Typing SVG" /></a>

</div>

# Social Engineering — AWARENESS · 🟡 MÉDIO

- **Status:** ✅ RESOLVIDO — três fragmentos com codificações diferentes, remontados na ordem do ataque.
- **Pontos:** 125 (valor dinâmico no momento da resolução)
- **Anexo:** `messages_internes.zip` (baixado como `internal.zip_messages`; 3 arquivos `.txt` em francês)
- **Enunciado:** *"Marc was fooled by an attack in several stages: a fake supplier, a fake technician, a fake maintenance agent. Each step left a fragment, encoded differently. Reconstruct the string to understand the attack."*
- **Flag:** `CyberZerk{Ch41n3_1ng3n13r13_S0c14l3_Br1s33}`

---

## TL;DR

1. O zip tem uma mensagem por etapa do ataque, cada uma com um fragmento.
2. Fornecedor → **Base64**, técnico → **ROT13**, agente → **Hex**.
3. Concatenar na ordem cronológica → *"Chaîne ingénierie sociale brisée"*.

## Análise

### Conteúdo do zip

```
messages_internes.zip
├── mail_fournisseur.txt   (426 B)
├── notes_standard.txt     (391 B)
└── chat_support.txt       (432 B)
```

Extraído numa pasta temporária fora do repo só para leitura (`unzip -l` antes, para ver o que havia dentro).

### As três etapas

| Hora (09/11) | Arquivo | Etapa | Fragmento | Codificação | Decodificado |
|---|---|---|---|---|---|
| 09:12 | `mail_fournisseur.txt` | Falso fornecedor, "fatura não paga" | `Q3liZXJaZXJre0NoNDFu` | Base64 | `CyberZerk{Ch41n` |
| 11:47 | `notes_standard.txt` | Falso técnico de TI ao telefone | `3_1at3a13e13_F0` | ROT13 | `3_1ng3n13r13_S0` |
| 16:05 | `chat_support.txt` | Falso "agente de manutenção" instalado | `6331346c335f4272317333337d` | Hex | `c14l3_Br1s33}` |

Como reconhecer cada uma:

- **Base64:** `Q3liZXJaZXJr` é sempre o Base64 de `CyberZerk` (visto no [Distress Signal](../DistressSignal/WRITEUP.md)).
- **Hex:** só `0–9a–f`, comprimento par, 2 caracteres por byte; `7d` = `}` → é o fragmento que fecha a flag.
- **ROT13:** dígitos e `_` parecem leet plausível, mas as letras (`a t a e F`) não formam nada → codificação que só mexe em letras (visto no [The Well-being Minute](../TheWellBeingMinute/WRITEUP.md)). `a↔n`, `t↔g`, `e↔r`, `F↔S`.

CyberChef: `From Base64`, `ROT13` (amount 13) e `From Hex`, um fragmento por vez.

### Remontagem

```
CyberZerk{Ch41n + 3_1ng3n13r13_S0 + c14l3_Br1s33}
= CyberZerk{Ch41n3_1ng3n13r13_S0c14l3_Br1s33}
```

Leet de *Chaîne ingénierie sociale brisée* ("cadeia de engenharia social quebrada"). Os cortes caem no meio das palavras (`Ch41n|3`, `S0|c14l3`), por isso nenhum fragmento isolado fazia sentido — a ordem vem dos horários das mensagens.

### Os sinais de engenharia social

| Etapa | Sinal |
|---|---|
| E-mail | Domínio *lookalike* `tricatel-fournisseur[.]ru` contra o legítimo `tricatel.fr`; urgência ("a entrega será suspensa") |
| Telefone | Pretexto de autoridade ("técnico de TI, infogerência"); ameaça ("o posto vai ser bloqueado"); pede para "validar um código" |
| Chat | Vítima instala um "agente de manutenção" = ferramenta de acesso remoto do atacante |

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Juntar o fragmento do meio sem decodificar (`3_1at3a13e13_F0`) | ✗ | Os dígitos/`_` enganam (parecem leet pronto), mas as letras estavam em ROT13 |

## Conclusão

Cada contato isolado parecia rotineiro (uma fatura, uma ligação do suporte, uma ferramenta de manutenção); só a cadeia inteira revela o golpe — exatamente como os fragmentos, que só fazem sentido juntos. Quebrar qualquer elo (checar o domínio, retornar a ligação por um número oficial, recusar instalar software pedido por telefone) teria parado o ataque.

---

## Apêndice — comandos

```bash
unzip -l messages_internes.zip
echo 'Q3liZXJaZXJre0NoNDFu' | base64 -d; echo                 # CyberZerk{Ch41n
echo '3_1at3a13e13_F0' | tr 'A-Za-z' 'N-ZA-Mn-za-m'            # 3_1ng3n13r13_S0
python3 -c "print(bytes.fromhex('6331346c335f4272317333337d').decode())"   # c14l3_Br1s33}
```
