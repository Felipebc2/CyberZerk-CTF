<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Reckless+Broadcast" alt="Typing SVG" /></a>

</div>

# Reckless Broadcast — CRYPTO · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — RSA com `e = 3` e mensagem pequena: `c = m³` sem redução modular, então basta uma raiz cúbica inteira
- **Pontos:** 125 (autor Perceval)
- **Anexo / Alvo:**
  - `broadcast.txt` (3042 bytes, sha256 `e3827728344590724786ffb3b0b9dc2922a6800f940150e9aaf1b9cc2e0db576`)
  - `README.txt` (o enunciado em francês, sha256 `53d4b4348f970dcc444f573fc4de84fc68196642e8d871a66aec4b85dc82cd82`)
- **Enunciado:** *"The DAF distributed the same encrypted memo to 3 recipients with e=3. broadcast.txt gives all three (n_i, c_i). Read the memo."*
- **Flag:** `CyberZerk{Hastad_br0adcast_3_d3st1nat41r3s_1_m3ss4g3}`

---

## TL;DR

1. Uma mensagem, 3 destinatários e `e = 3` apontam para o **ataque de broadcast de Håstad**: o CRT junta as 3 cifras em `m³` e uma raiz cúbica devolve `m`.
2. Aqui nem o CRT é preciso. Os três `c` são **idênticos** e têm 1267 bits, contra 2048 de cada `n`. Logo `m³ < n` e o `mod n` nunca agiu: `c = m³` é uma conta comum entre inteiros.
3. A raiz cúbica exata de `c` (dCode "Nth Root") convertida para bytes (CyberChef **To Base 16** → **From Hex**) dá a flag.

## Análise

### 1. Ler o anexo

`broadcast.txt` traz `e = 3` e três pares `(n_i, c_i)`. Comparando os tamanhos:

| Valor | Dígitos | Bits |
|---|---|---|
| `n1`, `n2`, `n3` | 617 cada | 2048 cada |
| `c1`, `c2`, `c3` | 382 cada | 1267 cada |

Duas coisas chamam atenção:

- **`c1 == c2 == c3`.** No RSA, `c = mᵉ mod n`. Com três `n` diferentes, os restos deveriam ser diferentes. Se são iguais, o `n` não influenciou o resultado.
- **`c` é bem menor que `n`.** Um `c` reduzido módulo um `n` de 2048 bits costuma ter perto de 2048 bits. Um `c` de 1267 bits é suspeito.

### 2. Por que `e = 3` é perigoso

O "mod n" só age quando `m³` passa de `n`, porque só aí sobra algo para reduzir. Se a mensagem é curta, `m³` fica abaixo de `n` e:

```
c = m³ mod n = m³          (nenhuma volta no relógio)
```

Aqui a mensagem tem 53 bytes, então `m` tem 423 bits e `m³` tem uns 1267 bits, menos que os 2048 bits de cada `n`. Isso explica as duas pistas: `c` tem exatamente o tamanho de `m³`, e é igual para os três destinatários porque não depende de `n`.

Nesse caso, desfazer a cifra é só tirar a **raiz cúbica inteira** de `c`, sem chave privada e sem fatorar `n`.

### 3. E o Håstad?

O ataque de Håstad é a versão geral do mesmo problema. Quando `m³` é maior que cada `n_i` mas menor que o produto `n1·n2·n3`, cada `c_i` sozinho foi reduzido. O **Teorema Chinês do Resto (CRT)** junta os três restos num único número `C ≡ m³ (mod n1·n2·n3)`. Como `m³ < n1·n2·n3`, vale `C = m³` sobre os inteiros, e a raiz cúbica dá `m`.

Neste desafio, o CRT devolveria o próprio `c`, já que os três restos são iguais e menores que cada `n`. O caso aqui é o **degenerado**: um destinatário só já bastava.

### 4. Raiz cúbica e conversão para texto

1. **dCode → "Nth Root"**:
   - Number = os 382 dígitos de `c1`.
   - Degree = `3`.
   - O resultado é um inteiro exato de 128 dígitos (`114186738326…857864573`). Conferi que elevado ao cubo ele dá exatamente `c1`.
2. **CyberChef**:
   - Entrada: o inteiro, numa linha só.
   - Receita: **To Base** (Radix 16) → **From Hex**.
   - O inteiro `m` é a mensagem com os bytes lidos em sequência (big-endian). Em hex, cada par vira um caractere.

```
CyberZerk{Hastad_br0adcast_3_d3st1nat41r3s_1_m3ss4g3}
```

Em francês: « Håstad broadcast : 3 destinataires, 1 message ».

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| WolframAlpha, modo Natural Language, `cuberoot(x)` | ✗ devolveu a fórmula `∛x` | `x` é uma variável. Serviu só para confirmar a sintaxe |
| WolframAlpha, Natural Language, `cuberoot(<c1>)` | ✗ "Wolfram\|Alpha doesn't understand your query" | O leitor de linguagem natural da versão gratuita não aceita um número de 382 dígitos. O problema é o tamanho da entrada, não a conta |
| WolframAlpha, modo Math Input, com o mesmo número | ✗ mesma mensagem | A mesma limitação de entrada. Pivotei para o dCode, que recebe o número e o grau em campos separados |

## Conclusão

RSA "de livro", sem padding, com expoente pequeno vaza a mensagem quando ela é curta: se `mᵉ < n`, a cifra é só uma potência comum e uma raiz inteira a desfaz. O broadcast de Håstad estende o ataque a mensagens maiores usando `e` cópias e o CRT, mas a causa é a mesma: a **mesma mensagem, sem padding aleatório**, cifrada com `e` pequeno. A defesa é usar padding (OAEP), que torna cada cifra diferente e faz `m` ocupar o tamanho de `n`. Lição prática: antes de montar o ataque completo, **compare os tamanhos** de `c` e `n` e veja se os `c` se repetem. Às vezes o atalho está no próprio arquivo.

---

## Apêndice — ferramentas

- **dCode "Nth Root":** Number = `c1`, Degree = `3`. Faz raiz exata de inteiros grandes.
- **CyberChef:** "To Base" (Radix 16) → "From Hex".
- **WolframAlpha:** não aceitou a entrada longa na versão gratuita.
- **Arsenal ctf-dispatch:**
  - `Arsenal/CRYPTO/rsa-common-attacks.md`, ramo "Håstad broadcast → CRT + e-th root".
  - Ferramenta citada: RsaCtfTool (`Manuals/RsaCtfTool/`).
