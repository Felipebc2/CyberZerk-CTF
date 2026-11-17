<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Hold+on" alt="Typing SVG" /></a>

</div>

# Hold on — AWARENESS · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — acróstico nas 12 linhas do relato; a dificuldade real foi o formato da flag.
- **Pontos:** 75 (valor dinâmico no momento da resolução)
- **Anexos:** `recit.txt` (baixado como `story.txt` no card; 12 linhas em francês) e `README.txt` (enunciado em francês)
- **Enunciado:** *"A text about the difficult weeks of Marc_V. Really worth reading: it carries, implicitly, a message addressed to it — and which is also the flag."*
- **Flag:** `CyberZerk{TUNESPASSEUL}`

---

## TL;DR

1. `recit.txt` é um relato de 12 linhas, uma frase por linha, sobre Marc esgotado e isolado.
2. "En filigrane" (nas entrelinhas) → a mensagem está na **forma**, não no conteúdo: **acróstico**, a primeira letra de cada linha.
3. `TUNESPASSEUL` = *"Tu n'es pas seul"* ("você não está sozinho") → enviada crua, sem separadores.

## Análise

### Triagem: não é estego de bytes

`cat -A` nos dois arquivos: nada de espaço sobrando no fim de linha, zero-width ou caracteres de controle — só acentos UTF-8 e travessões. A mensagem não está escondida nos bytes, está na estrutura do texto.

A palavra-chave do `README.txt` original:

> *"Lisez-le vraiment : il porte, **en filigrane**, un message qui lui est adressé — et qui est aussi le flag."*

Filigrana = a marca d'água do papel, que só aparece quando se olha a folha contra a luz em vez de ler. Num texto de uma frase por linha, o lugar clássico disso é a vertical da margem.

### Acróstico

```bash
cut -c1 Awareness/HoldOn/recit.txt | tr -d '\n'; echo
# -> TUNESPASSEUL
```

| # | Início da linha | Letra |
|---|---|---|
| 1 | **T**ard le soir, Marc reste encore devant son écran… | T |
| 2 | **U**n poids qu'il n'arrive plus à nommer… | U |
| 3 | **N**e rien dire lui semble plus simple… | N |
| 4 | **E**t pourtant, le silence ne l'allège pas… | E |
| 5 | **S**es collègues remarquent sa fatigue… | S |
| 6 | **P**ersonne n'attend de lui qu'il aille bien… | P |
| 7 | **A**u fond, demander de l'aide n'est pas un aveu de faiblesse. | A |
| 8 | **S**e confier à une personne de confiance… | S |
| 9 | **S**'arrêter, souffler, consulter… | S |
| 10 | **E**ntendre ce que le corps et l'esprit réclament… | E |
| 11 | **U**n premier mot suffit parfois… | U |
| 12 | **L**à, maintenant, il peut encore tendre la main… | L |

`TU N'ES PAS SEUL` — o `N` sozinho é a elisão de *ne* diante de *es*. O `cut -c1` é seguro aqui porque nenhuma linha começa com letra acentuada (um `É` inicial ocuparia 2 bytes).

"Endereçada a ele": o relato fala **sobre** Marc na 3ª pessoa (*il*, *lui*), enquanto a vertical fala **com** ele na 2ª pessoa (*tu*) — o recado que, como diz a linha 5, os colegas não sabem como dar.

### Formato da flag

As flags anteriores do CTF trocam espaços e apóstrofos por `_` (`J_AI_LU_ET_J_ACCEPTE…` ← *J'ai lu et j'accepte*; `C_3st_N0n` ← *C'est non*). Seguindo esse padrão, a primeira tentativa foi `TU_N_ES_PAS_SEUL` — recusada. O formato aceito é o mais literal: as 12 letras cruas do acróstico, sem separadores. O enunciado não especifica o formato; mandamos feedback à organização sugerindo explicitá-lo.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Estego em bytes (espaços no fim, zero-width) | ✗ | `cat -A` limpo; só acentos e travessões |
| `CyberZerk{TU_N_ES_PAS_SEUL}` | ✗ Incorrect | Inferi a regra "apóstrofo/espaço → `_`" das outras flags e dei peso demais a ela; esta flag usa as letras do acróstico sem nenhuma transformação |

## Conclusão

A mecânica é trivial (acróstico); a lição é o conteúdo: diante do esgotamento, pedir ajuda não é fraqueza e "você não está sozinho". A armadilha técnica foi só o formato — quando uma flag é extraída de um texto, a forma crua do que se extraiu é a primeira a testar, antes de qualquer convenção inferida de outros desafios.

---

## Apêndice — comando

```bash
cut -c1 Awareness/HoldOn/recit.txt | tr -d '\n'; echo
```
