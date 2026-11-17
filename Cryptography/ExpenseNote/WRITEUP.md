<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Expense+Note" alt="Typing SVG" /></a>

</div>

# Expense Note — CRYPTO · 🟢 EASY

- **Status:** ✅ RESOLVIDO — Base64 seguido de Vigenère com chave `FOLACE`
- **Pontos:** 75 (autor Perceval)
- **Anexo / Alvo:** `note_chiffree.txt` (69 bytes, sha256 `01252471e8bc217d588b0280ab0dcee702611dd26cd68856ca84695126866684`)
- **Enunciado:** *"The DAF calculates its expense reports "so that no one sticks their nose in". A burned-out intern leaked this note before resigning. It would prove that CODIR bonuses exploded while leave was refused."*
- **Flag:** `CyberZerk{Pr1m3s_CODIR_P3nd4nt_L3s_R3fus_D3_C0ng3s}`

---

## TL;DR

1. O anexo é **Base64**. Decodificado, vira `HmmetDjfv{...}`, que ainda está cifrado.
2. Os símbolos e números ficam intactos e duas letras diferentes viram a mesma (`y` e `b` → `m`). Então é uma cifra **polialfabética**: Vigenère.
3. Decifrar `HmmetDjfv` usando `CyberZerk` como chave entrega a chave verdadeira, `FOLACEFOL`. Ela repete a cada 6 letras, então a chave é `FOLACE`. Com ela sai a flag.

## Análise

### 1. Camada Base64

```
SG1tZXREamZ2e1B0MXEzeF9RWkRLVl9VM2JvNG52X1AzeF9GM3F1dV9IM19IMGJyM3N9
```

O alfabeto é `A–Za–z0–9` e o prefixo `SG1t` é típico de Base64 (veja o desafio [Le Chiffrement Militaire](../MilitaryEncryption/WRITEUP.md)). No CyberChef, **From Base64** dá:

```
HmmetDjfv{Pt1q3x_QZDKV_U3bo4nv_P3x_F3quu_H3_H0br3s}
```

Ainda não é a flag. Tem o formato `XXXXXXXXX{...}`, mas as letras estão embaralhadas.

### 2. Identificar a cifra

| Pista | Leitura |
|---|---|
| `{`, `_`, `}` e os números (`1`, `3`, `4`, `0`) no lugar | cifra que só mexe em **letras** |
| `HmmetDjfv` tem 9 letras, como `CyberZerk` | o formato da flag sobrevive, o que permite usar texto claro conhecido |
| `y` → `m` e `b` → `m` | duas letras diferentes viram a mesma, o que **descarta** César e substituição monoalfabética (cada letra teria um só substituto) |

Portanto é uma cifra **polialfabética**, em que o deslocamento depende da posição. O candidato natural é o Vigenère.

### 3. Recuperar a chave por texto claro conhecido

No Vigenère, `chave = (cifra − claro) mod 26`, e essa é a **mesma operação que o decodificador faz**. Então, em vez de fazer a conta letra a letra, basta decifrar a cifra usando o texto claro conhecido como "chave":

```
cifra:   H m m e t D j f v
"chave": C y b e r Z e r k
saída:   F O L A C E F O L    ← esta é a chave verdadeira
```

A sequência repete depois de 6 letras (`FOLACE` | `FOL...`), então o **período é 6**: chave `FOLACE`.

### 4. Decifrar

Vigenère Decode do texto inteiro com a chave `FOLACE`, preservando caixa e símbolos:

```
CyberZerk{Pr1m3s_CODIR_P3nd4nt_L3s_R3fus_D3_C0ng3s}
```

Em francês: « Primes CODIR pendant les refus de congés » (bônus do CODIR enquanto as férias eram recusadas). Bate com o enunciado. Atenção: o `0` em `C0ng3s` é **zero**, como na cifra (`H0br3s`), porque o Vigenère não altera números.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| dCode com "Knowing only a partial key" = `CYBERZERK` | ✗ texto ilegível, **mas** as 9 primeiras letras saíram `FOLACEFOL` | Usou `CyberZerk` como chave, e não como texto claro. Sem querer, isso aplicou o truque da seção 3 e revelou a chave |
| Chave `FOLACEFOL` (9 letras) | ✗ só `CY BER ZER K` saiu certo, o resto virou lixo | O período real é 6. Com 9 letras, a chave desalinha a partir da 10ª letra, que deveria usar `A` e usou `F` |
| Chave `FOLACE` no dCode | ✓ letras certas, mas tudo maiúsculo e símbolos trocados por espaços | O dCode descarta caixa e pontuação. A flag foi montada num decodificador com a opção "Manter tudo" |

## Conclusão

São duas camadas: uma **codificação** (Base64, sem segredo) e uma **cifra** clássica (Vigenère). A lição principal é o ataque com texto claro conhecido: como toda flag começa com `CyberZerk`, decifrar o começo da cifra usando esse texto como chave revela a chave real, e o ponto onde ela se repete dá o período. Errar o período por excesso (`FOLACEFOL`) produz um padrão reconhecível: o trecho inicial sai certo e o resto desanda.

---

## Apêndice — ferramentas

- CyberChef: "From Base64" → "Vigenère Decode" (key `FOLACE`). O CyberChef preserva caixa e símbolos.
- dCode Vigenère Cipher: as opções "Knowing a plaintext word" (`CyberZerk`) ou "Knowing the Key" (`FOLACE`). A saída sai sem caixa e sem símbolos.
- Decodificador online de Vigenère com a opção "Manter tudo", usado para a flag final.
- Shell para a 1ª camada: `base64 -d note_chiffree.txt`
