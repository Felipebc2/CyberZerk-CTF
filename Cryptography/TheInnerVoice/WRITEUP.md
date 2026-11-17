<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=La+Voix+Int%C3%A9rieure" alt="Typing SVG" /></a>

</div>

# La Voix Intérieure — CRYPTO · 🟢 EASY

- **Status:** ✅ RESOLVIDO — Vigenère com chave `JESUISNUL`, tirada do próprio enunciado
- **Pontos:** 100 (Intro, autor Perceval)
- **Anexo / Alvo:** nenhum; o texto cifrado vem no enunciado
- **Enunciado:** *"Extrait du journal de bord de l'analyste - Jour 43. « Je n'arrive plus à avancer. [...] Elle me répète sans cesse la même chose, en boucle, comme une fatalité : je suis nul. » [...] Mon propre message d'espoir a été chiffré par sa rengaine, utilisant une méthode de substitution séculaire attribuée à un diplomate français du 16ème siècle. Voici la note que j'ai retrouvée ce matin sur mon bureau : `LctyzRrlv{Cy_Sm_Bs_Cflli_Awq}`"*
- **Flag:** `CyberZerk{Tu_As_Ta_Place_Ici}`

---

## TL;DR

1. O "diplomata francês do século XVI" com uma "substituição" é **Blaise de Vigenère**, então a cifra é a **de Vigenère**.
2. A chave é a "rengaine" (o refrão) que a voz repete em loop: **« je suis nul »**, que vira `JESUISNUL` só com as letras.
3. Para confirmar a chave sem chute, usamos o texto claro conhecido `CyberZerk`. Depois foi só decifrar no decodificador online, mantendo os símbolos.

## Análise

### 1. Identificar a cifra

O enunciado dá três pistas:

| Pista | Leitura |
|---|---|
| "substitution séculaire", "diplomate français du 16ème siècle" | Blaise de Vigenère (1523–1596) |
| "en boucle", "répète sans cesse la même chose" | chave curta que se **repete** ao longo do texto |
| `LctyzRrlv{...}` preserva maiúsculas, minúsculas, `{`, `_` e `}` | cifra só de letras; o formato `CyberZerk{...}` (9 letras) sobrevive |

**Como o Vigenère funciona:** cada letra do texto claro é deslocada pela letra correspondente da chave (A=0, B=1, ..., Z=25). Quando a chave acaba, ela recomeça do início:

```
cifra  = (claro + chave) mod 26
claro  = (cifra − chave) mod 26
chave  = (cifra − claro) mod 26     ← ataque com texto claro conhecido
```

Os caracteres que não são letras (`{`, `_`, `}`) passam direto e **não consomem** posição da chave.

### 2. Recuperar a chave pelo texto claro conhecido

Toda flag começa com `CyberZerk`, então os 9 primeiros caracteres do claro são conhecidos. Subtraindo letra por letra:

| cifra | claro | conta (mod 26) | chave |
|---|---|---|---|
| L (11) | C (2) | 9 | **J** |
| c (2) | y (24) | −22 → 4 | **E** |
| t (19) | b (1) | 18 | **S** |
| y (24) | e (4) | 20 | **U** |
| z (25) | r (17) | 8 | **I** |
| R (17) | Z (25) | −8 → 18 | **S** |
| r (17) | e (4) | 13 | **N** |
| l (11) | r (17) | −6 → 20 | **U** |
| v (21) | k (10) | 11 | **L** |

O resultado é `JESUISNUL`, exatamente o « je suis nul » do enunciado. A hipótese da chave fica confirmada pelo próprio texto cifrado, não por chute.

### 3. Decifrar

No decodificador online de Vigenère usei a chave `jesuisnul` com a opção **Manter tudo**, para preservar `{`, `_` e `}`. O resto da mensagem recomeça a chave do `J`:

```
Cy_Sm_Bs_Cflli_Awq
JE SU IS NULJE SUI
Tu_As_Ta_Place_Ici
```

A mensagem secreta é « Tu as ta place ici » (você tem o seu lugar aqui), a resposta otimista ao « je suis nul ».

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| chave `voice` | ✗ saiu `QolwvWddt{Yd_Ee_Zo_Hrdje_Fii}` | "voice" é **quem** fala, não **o que** a voz diz. A 1ª letra já derruba a hipótese: `L − V = 11 − 21 = −10 → 16 = Q ≠ C` |

## Conclusão

Este é um Intro de leitura atenta. O enunciado nomeia a cifra por perífrase (o diplomata Vigenère) e esconde a chave na narrativa (o refrão "je suis nul"). A lição que fica: quando o formato da flag é conhecido, o **ataque com texto claro conhecido** (`chave = cifra − claro`) transforma o chute da chave numa verificação objetiva. Bastam as 2 ou 3 primeiras letras para confirmar ou derrubar uma hipótese.

---

## Apêndice — ferramentas

- Decodificador online de Vigenère (chave `jesuisnul`, opção "Manter tudo"). Alternativas equivalentes: CyberChef "Vigenère Decode" e dCode.
