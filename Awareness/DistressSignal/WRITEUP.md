<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Distress+Signal" alt="Typing SVG" /></a>

</div>

# Distress Signal — AWARENESS · 🟢 FÁCIL (Intro)

- **Status:** ✅ RESOLVIDO — decodificação Base64 direta no CyberChef.
- **Pontos:** 100 (valor dinâmico no momento da resolução; challenge Intro, sem troféu de first blood)
- **Anexo:** — (a string vem no próprio enunciado)
- **Enunciado:** *"Alex has been carrying out audit missions for 8 months without any real interruption. Yesterday, after a critical error on a production at 3 a.m., he cut off all his network access. In his activity logs, only one unusual message encoded in Base64 was found: `Q3liZXJaZXJre0xlX2J1cm5fb3V0X25lc3RfcGFzX3VuZV9mYWlibGVzc2V9`. Decode this message."*
- **Flag:** `CyberZerk{Le_burn_out_nest_pas_une_faiblesse}`

---

## TL;DR

1. O enunciado entrega uma string e diz que é Base64.
2. `From Base64` no CyberChef (ou `base64 -d`).
3. Sai a flag: *"Le burn-out n'est pas une faiblesse"* ("o burn-out não é uma fraqueza").

## Análise

### Base64 em uma página

Base64 é **codificação, não cifra**: não há chave, qualquer um reverte. Serve para transportar bytes arbitrários como texto (e-mail, JSON, URL, logs) usando 64 símbolos (`A–Z a–z 0–9 + /`, `=` como padding).

- 64 = 2⁶ → cada caractere carrega **6 bits**; **3 bytes = 4 caracteres**.
- A string tem 60 caracteres → 60 / 4 × 3 = **45 bytes**. Como 45 é múltiplo de 3, o último bloco é completo e **não há `=`**.

### Reconhecer de olho

`Q3liZXJaZXJr` é sempre o Base64 de `CyberZerk` — o prefixo fixo da flag gera um prefixo fixo codificado. Vale guardar: achar `Q3liZXJaZXJr` em qualquer log, cookie ou arquivo já indica uma flag Base64.

### Decodificação

CyberChef: Input = a string → `From Base64` (alfabeto padrão).

```
CyberZerk{Le_burn_out_nest_pas_une_faiblesse}
```

O apóstrofo de *n'est* sumiu na flag (`nest`), como as 12 letras cruas do [Hold on](../HoldOn/WRITEUP.md).

## Conclusão

Challenge Intro: a mecânica é uma operação só e o peso está na mensagem — esgotamento contínuo não é fraqueza, e existem linhas de escuta (*"you are not alone"*, o mesmo recado do acróstico de Hold on).

---

## Apêndice — comando

```bash
echo 'Q3liZXJaZXJre0xlX2J1cm5fb3V0X25lc3RfcGFzX3VuZV9mYWlibGVzc2V9' | base64 -d; echo
# -> CyberZerk{Le_burn_out_nest_pas_une_faiblesse}
```
