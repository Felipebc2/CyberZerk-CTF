<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Turnkey" alt="Typing SVG" /></a>

</div>

# Turnkey (Clé en main) — CRYPTO · 🔴 DIFFICULT

- **Status:** ✅ RESOLVIDO — RSA com primos **próximos demais**: fatoração de **Fermat** em 0 passos
- **Pontos:** 175 (autor Perceval, 262 solves)
- **Anexo:**
  - `cle_publique_et_message.txt` (696 bytes, sha256 `d271878543bf142fb79f4c3cb35fa9b3d84d71923b9354ca3a7f88849637d4af`) — traz `n`, `e = 65537` e `c`
- **Enunciado:** *"The DAF's RSA public key and an encrypted message were intercepted. The 'in-house' key generator was hastily coded one night of production... the first two factors look strangely similar."*
- **Flag:** `CyberZerk{F3rm4t_C4ss3_L3s_Pr3m13rs_Tr0p_Pr0ch3s}`

---

## TL;DR

1. `e = 65537` (grande) elimina os ataques de expoente pequeno. Com `n` de 1023 bits, o caminho é **fatorar `n`** — normalmente inviável, mas a dica entrega a fraqueza.
2. *"the first two factors look strangely similar"* = os primos `p` e `q` foram gerados **colados** (gerador caseiro às pressas). Primos próximos → **fatoração de Fermat**.
3. O `solve.py` (só `stdlib`: `math.isqrt`) acha `p,q` em **0 iterações**, reconstrói `d` e decifra `c`. `p − q = 839384` para primos de 512 bits — distância ridícula.

## Análise

### 1. Ler os parâmetros antes de chutar o ataque

O arquivo entrega `n`, `e` e `c`. A primeira coisa num RSA é **medir**:

| Valor | Bits | Leitura |
|---|---|---|
| `n` | 1023 | grande demais pra fatorar na força bruta / factordb |
| `e` | 17 (`65537`) | expoente **padrão** e grande → descarta cube-root, Håstad, Wiener |
| `c` | 1022 | mensagem cifrada normal |

Com `e = 65537`, os atalhos de expoente pequeno (como no *Reckless Broadcast*, `e=3`) não valem. Sobra atacar a chave por onde ela é frágil: **a geração dos primos**. E é exatamente aí que a dica aponta.

### 2. Por que "primos próximos" quebra o RSA

Decifrar RSA exige `d = e⁻¹ mod φ(n)`, com `φ(n) = (p−1)(q−1)`. Isso só sai conhecendo `p` e `q`. A segurança do RSA é justamente `n = p·q` ser difícil de fatorar — **desde que `p` e `q` sejam bem distantes e aleatórios**.

Quando o gerador é preguiçoso e produz `p` e `q` **próximos** (ex.: `q = nextprime(p)`), a fatoração vira trivial via **Fermat**.

### 3. A mecânica de Fermat

Todo `n` ímpar é uma diferença de quadrados: `n = a² − b² = (a−b)(a+b)`. Casando com `n = p·q`:

```
a = (p + q) / 2      (a média dos primos)
b = (p − q) / 2      (metade da distância entre eles)
```

O método chuta `a` a partir de `⌈√n⌉` e sobe de 1 em 1 até `a² − n` ser um quadrado perfeito (= `b²`):

```python
from math import isqrt
a = isqrt(n) + 1
while True:
    b2 = a*a - n
    b = isqrt(b2)
    if b*b == b2:        # achou
        break
    a += 1
p, q = a + b, a - b
```

Se `p` e `q` são próximos, `b` é pequeno, logo `a = (p+q)/2` fica **logo acima de `√n`** e o loop fecha em pouquíssimos passos. Aqui fechou em **0 passos**: `⌈√n⌉` já era exatamente `(p+q)/2`.

### 4. Recuperar `d` e decifrar

Com os primos na mão, a chave privada se reconstrói direto:

```python
phi = (p - 1) * (q - 1)
d   = pow(e, -1, phi)          # inverso modular (Python 3.8+)
m   = pow(c, d, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
```

```
[+] fatorado em 0 passos
[+] flag: CyberZerk{F3rm4t_C4ss3_L3s_Pr3m13rs_Tr0p_Pr0ch3s}
```

### 5. O tamanho da falha, em números

```
p = ...44177119922983875200034814456503
q = ...44177119922983875200034813617119
p − q = 839384        (para primos de 512 bits)
```

Uma diferença de ~840 mil entre números de 155 dígitos. Isso é a assinatura de `q = nextprime(p)` (ou similar): o gerador caseiro gerou um primo e pegou o "próximo", deixando os dois praticamente colados.

Em francês: « **Fermat casse les premiers trop proches** » — "Fermat quebra os primos próximos demais". O nome do flag é o próprio diagnóstico.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| Usar o **RsaCtfTool** (`--attack fermat`), a ferramenta "oficial" do Arsenal | ✗ não rodou | O venv (`~/ctf-venv`) tinha sido movido pra uma pasta de lixeira; o shebang apontava pro caminho antigo e faltava `sympy`. Reviver o venv era mais trabalho que o ataque |
| — (pivot) | ✓ | Fermat é tão simples que a `stdlib` resolve: `math.isqrt` aguenta inteiros gigantes e `pow(e,-1,phi)` faz o inverso modular. Zero dependências |

## Conclusão

A segurança do RSA mora na dificuldade de fatorar `n` — mas isso **assume primos grandes, aleatórios e distantes**. Um gerador que escolhe `p` e depois o primo "seguinte" como `q` destrói essa premissa: `p ≈ q`, e a fatoração de Fermat (`n = a²−b²` com `a ≈ √n`) acha os dois quase instantaneamente, sem chave privada. A defesa é gerar `p` e `q` **independentes** e verificar que `|p−q|` é grande. Lição prática de leitura de desafio: antes de montar qualquer ataque, **meça `e` e `n`** — `e` grande manda fatorar, e qualquer pista de "primos parecidos / gerados juntos" é sinal verde pra Fermat. E quando a ferramenta de referência está quebrada, a `stdlib` costuma bastar.

---

## Apêndice — ferramentas

- `solve.py` — `python3 solve.py`: fatoração de Fermat + reconstrução de `d` + decifra. Só biblioteca padrão (`math.isqrt`, `pow(e,-1,phi)`). Imprime os passos e para sozinho; se passar de milhões de passos, não é Fermat (seria multi-primo).
- Arsenal ctf-dispatch: `Arsenal/CRYPTO/rsa-common-attacks.md` — linha *"`p` and `q` close → Fermat"*. Ferramenta citada: RsaCtfTool (`--attack fermat`), que faz esse mesmo loop por baixo.
