<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=The+DAF's+Chest" alt="Typing SVG" /></a>

</div>

# The DAF's Chest (Le Coffre du DAF) — CRYPTO · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — XOR com chave repetida `TRICATEL`
- **Pontos:** 100 (autor Perceval)
- **Anexo / Alvo:** `coffre_chiffre.hex` (81 bytes = 80 caracteres hex + quebra de linha, ou seja, 40 bytes de cifra; sha256 `0706cafdc33c0e69f8ea37312b196b112aef37b5e8f9f65cedbe9ce6d1fbef03`). Na plataforma o arquivo aparece traduzido como `chest_number.hex`
- **Enunciado:** *"The DAF "encrypted" the contents of his trunk with a small in-house script. We retrieved the result in hexadecimal. It seems that he always reuses the same key, over and over again."*
- **Flag:** `CyberZerk{X0R_R3p3t3_C_3st_P4s_S3cur1s3}`

---

## TL;DR

1. "Script caseiro", saída em hex e "a mesma chave, de novo e de novo" indicam um **XOR com chave repetida**.
2. O XOR desfaz a si mesmo: `cifra ⊕ claro = chave`. Como a flag começa com `CyberZerk{`, usar esse texto como chave no CyberChef revela o começo da chave real: `TRICATELTR`.
3. `TR` reaparece depois de 8 letras, então o período é 8 e a chave é `TRICATEL`. Com ela sai a flag.

## Análise

### 1. Ler o anexo

```
172b2b26330e203e3f291173130b177f24613d701e171a7f2726161375271a1f67313c3170277631
```

São só caracteres `0–9a–f`, então é **hexadecimal**: cada par representa 1 byte. São 80 caracteres, portanto 40 bytes. No CyberChef, **From Hex** transforma em bytes, e a saída é ilegível, porque ainda está cifrada.

### 2. Identificar a cifra

| Pista | Leitura |
|---|---|
| "petit script maison" | cifra caseira e simples, não AES ou RSA |
| saída em hex | os bytes cifrados não são imprimíveis. O XOR gera bytes quaisquer, por isso precisa de hex para virar texto |
| "toujours la même clé, encore et encore" | **chave repetida**: uma chave curta, repetida ao longo da mensagem inteira |

É o **XOR com chave repetida**, o "Vigenère binário". O Vigenère soma letras módulo 26. O XOR combina bytes bit a bit, e cada byte da chave é usado em ciclo.

### 3. Por que o texto conhecido entrega a chave

O XOR é **sua própria inversa**: `a ⊕ b ⊕ b = a`. Daí:

```
cifra = claro ⊕ chave   ⇒   chave = cifra ⊕ claro
```

Toda flag começa com `CyberZerk{` (10 bytes). Então um **XOR** com a chave `CyberZerk{` (UTF8) depois do From Hex deixa a chave real nos 10 primeiros bytes da saída:

```
saída: TRICATELTR R
       └── 10 bytes ─┘└ 11º byte: coincidência
```

Só os 10 primeiros bytes valem, porque é o tamanho do texto conhecido. Do 11º byte em diante o CyberChef volta ao começo de `CyberZerk{` e aplica esses bytes a uma parte da flag que não é `CyberZerk{`.

### 4. Achar o período e decifrar

Em `TRICATELTR`, o `TR` volta logo depois de `TRICATEL`. É a chave recomeçando o ciclo, então o **período é 8** e a chave é **`TRICATEL`**, o nome da empresa fictícia do CTF.

From Hex → XOR com a chave `TRICATEL` (UTF8):

```
CyberZerk{X0R_R3p3t3_C_3st_P4s_S3cur1s3}
```

Em francês: « XOR répété, c'est pas sécurisé ».

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| XOR com a chave `TRICATELTRR` (11 bytes) | ✗ `CyberZerk{C'ABT>p$q$LEN-neWG0k...`: só os 11 primeiros caracteres saíram certos | Período errado, o mesmo erro do `FOLACEFOL` no [Expense Note](../ExpenseNote/WRITEUP.md). A chave de 11 bytes coincide com a real só até o 11º byte e desalinha a partir do 12º, que deveria usar o 4º byte da chave (`C`) e usou o 1º (`T`). Além disso, o último `R` nem era chave, era a coincidência do 11º byte |

## Conclusão

Um XOR com chave curta e repetida tem as mesmas fraquezas do Vigenère. Um texto claro conhecido do tamanho de um período (aqui, o prefixo `CyberZerk{`, 10 bytes ≥ 8) entrega a chave inteira, porque `cifra ⊕ claro = chave`. O XOR só é seguro quando a chave é aleatória, do tamanho da mensagem e nunca reutilizada (one-time pad), justamente o que o DAF não fez. Lição prática repetida: depois de extrair o fluxo de chave, procure onde ele **se repete** e corte ali. Usar o fluxo inteiro como chave dá um começo certo seguido de lixo.

---

## Apêndice — ferramentas

- CyberChef: "From Hex" → "XOR" (key `CyberZerk{`, UTF8) para revelar a chave; depois "XOR" (key `TRICATEL`, UTF8) para a flag.
- Arsenal ctf-dispatch: `Arsenal/CRYPTO/xor-repeating-key.md`.
