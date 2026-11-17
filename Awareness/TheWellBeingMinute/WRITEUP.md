<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=The+Well-being+Minute" alt="Typing SVG" /></a>

</div>

# The Well-being Minute — AWARENESS · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — ROT13 (César com deslocamento 13) sobre a flag no fim do fil.
- **Pontos:** — (valor dinâmico; preencher)
- **Anexo:** `minute_bienetre.txt` (export de um canal de chat interno, em francês)
- **Enunciado:** *canal `#minute-bien-etre` da empresa fictícia Tricatel — um colaborador (Marc_V) esgotado deixa uma mensagem cifrada antes de parar de responder.*
- **Flag:** `CyberZerk{R3p3r3_La_M4nipul4t10n_R3st3_Hum41n}`

---

## TL;DR

1. O arquivo é um fil de chat satírico sobre management tóxico (presença obrigatória na "minuto bem-estar", 60h/semana, culpa por arrests maladie).
2. Marc_V deixa `PloreMrex{E3c3e3_Yn_Z4avchy4g10a_E3fg3_Uhz41a}` e dá a pista: *"Juste un décalage... il suffit de le remettre droit"* → é só um deslocamento.
3. `PloreMrex` é `CyberZerk` deslocado 13 → aplicar **ROT13** devolve a flag.

## Análise

### A pista

O próprio texto entrega o vetor duas vezes:

> *"Vous reconnaîtrez le procédé, il traîne partout dans ces messages"*
> *"Ce n'est pas un code d'expert. Juste un décalage, comme le discours de la Direction : il suffit de le remettre droit."*

"Un décalage" = cifra de César. Reconhecer o prefixo fecha o deslocamento sem brute-force: todo flag é `CyberZerk{...}`, e o ciphertext começa com `PloreMrex{` → `P→C` é um recuo de 13, ou seja **ROT13** (que é César 13, auto-inverso).

### Decifração

ROT13 só mexe em letras; dígitos e `_` passam intactos (é por isso que a flag "leetada" sobrevive ao round-trip):

| Cipher | ROT13 |
|---|---|
| `PloreMrex` | `CyberZerk` |
| `E3c3e3` | `R3p3r3` |
| `Yn` | `La` |
| `Z4avchy4g10a` | `M4nipul4t10n` |
| `E3fg3` | `R3st3` |
| `Uhz41a` | `Hum41n` |

Resultado: `CyberZerk{R3p3r3_La_M4nipul4t10n_R3st3_Hum41n}` — "Repère la manipulation, reste humain". O conteúdo da flag é a própria mensagem de awareness.

## Conclusão

Challenge de conscientização: a mecânica (ROT13) é trivial e serve de embrulho para a mensagem. O prefixo conhecido `CyberZerk{` dispensa qualquer tentativa dos 25 deslocamentos.

---

## Apêndice — comando

ROT13 em uma linha, sem script dedicado:

```bash
echo 'PloreMrex{E3c3e3_Yn_Z4avchy4g10a_E3fg3_Uhz41a}' | tr 'A-Za-z' 'N-ZA-Mn-za-m'
# -> CyberZerk{R3p3r3_La_M4nipul4t10n_R3st3_Hum41n}
```
