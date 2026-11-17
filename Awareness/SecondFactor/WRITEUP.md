<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Second+Factor" alt="Typing SVG" /></a>

</div>

# Second Factor — AWARENESS · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — TOTP (HMAC-SHA1, 30 s, 6 dígitos) calculado passo a passo no CyberChef.
- **Pontos:** 75 (valor dinâmico no momento da resolução)
- **Anexo:** `second-facteur-README.txt` (texto, em francês)
- **Enunciado:** *"The portal switches to TOTP (SHA-1, 30 s, 6 digits). Secret base32 provided. What code is valid at the given Unix T time? Flag = CyberZerk{2fa_}."*
- **Flag:** `CyberZerk{2fa_053377}`

---

## TL;DR

1. O anexo entrega tudo: segredo base32 `JBSWY3DPEHPK3PXP` e instante `T = 1762900000`.
2. TOTP = HOTP com contador `C = floor(T / 30)` → HMAC-SHA1(segredo, C em 8 bytes big-endian) → truncagem dinâmica → `mod 10^6`.
3. Código `053377` (com o zero à esquerda!) → `CyberZerk{2fa_053377}`.

## Análise

O arquivo:

```
Le portail RH passe à la double authentification (TOTP, SHA-1, 30 s, 6 chiffres).
Secret (base32) : JBSWY3DPEHPK3PXP
Quel code est valide à l'instant Unix T = 1762900000 ?
Le flag est CyberZerk{2fa_<code>} (ex. CyberZerk{2fa_123456}).
```

Não há alvo nem vulnerabilidade: é implementar a RFC 6238 corretamente. Feito no CyberChef, uma operação por vez, para ver cada peça.

### 1. Segredo base32 → bytes (chave do HMAC)

Base32 = alfabeto `A–Z2–7`, **5 bits por caractere**. 16 caracteres × 5 = 80 bits = **10 bytes**.

CyberChef: `From Base32` → `To Hex`

```
Hello!Þ­¾ï  →  48 65 6c 6c 6f 21 de ad be ef
```

O segredo é literalmente `"Hello!"` + `0xDEADBEEF` — o segredo de exemplo usado em meia internet de documentação de TOTP. Só aparecem 3 caracteres "estranhos" para 4 bytes porque `0xAD` é o *soft hyphen* do Latin-1, invisível. Chave do HMAC: `48656c6c6f21deadbeef`.

### 2. Tempo → contador

```
C = floor((T - T0) / X) = floor(1762900000 / 30) = 58763333 = 0x380a845
```

CyberChef: `Divide` (input `1762900000 30`, delimitador Space) → `58763333.333…`; só a **parte inteira** conta. `To Base` radix 16 → `380a845`. A janela de 30 s faz o código ficar estável e tolerar pequeno desvio de relógio.

A RFC 4226 exige o contador como **inteiro de 8 bytes big-endian** → padding com zeros à esquerda:

```
000000000380a845
```

### 3. HMAC-SHA1(chave, contador)

CyberChef: input `000000000380a845` → `From Hex` → `HMAC` (Key `48656c6c6f21deadbeef`, tipo **HEX**, função **SHA1**).

```
2c0d7063c651851cb50d4efd9cb7fc1f2d29412f   (20 bytes)
```

O `From Hex` é indispensável: sem ele o HMAC é calculado sobre o *texto* ASCII de 16 caracteres, não sobre os 8 bytes do contador.

### 4. Truncagem dinâmica → 6 dígitos

| Etapa | Valor |
|---|---|
| Offset = **último nibble** do HMAC (`…2f` → `f`) | 15 |
| 4 bytes a partir do índice 15 (índices 15–18) | `1f 2d 29 41` |
| `& 0x7FFFFFFF` (primeiro byte `1f` < `0x80` → sem efeito) | `0x1f2d2941` |
| Decimal (`From Base` radix 16) | 523053377 |
| `mod 1000000` (`MOD` no CyberChef) | 53377 |
| **Padding a 6 dígitos** | **`053377`** |

O offset é um nibble (0–15) para que offset + 4 nunca passe do byte 19. A máscara zera o bit de sinal para que implementações com inteiro de 32 bits com sinal deem o mesmo resultado.

Conferido por um caminho independente (Python stdlib: `base64` + `hmac` + `struct`) — HMAC, offset, bytes e código idênticos. Flag aceita na plataforma.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Usar a operação `Generate TOTP` do CyberChef | ✗ (descartada) | Calcula para o relógio atual; não permite fixar `T` |
| `To Base` radix 16 sobre `58763333.333…` | ✗ | Converteu também a fração (`.5555…` = 1/3 em hex); o contador é só a parte inteira |
| Offset = último **byte** (`2f` = 47) | ✗ | O offset é o último **nibble** (`f` = 15); 47 apontaria fora dos 20 bytes |
| Ler os 4 bytes a partir de `fc` / `c6` | ✗ | Erro de contagem na tabela de índices; o correto começa no índice 15 (`1f`) |
| Flag `Cyberzerk{2fa_53377}` | ✗ (corrigida antes de enviar) | Faltou o zero à esquerda (o TOTP é string de 6 dígitos, não número) e o `Z` maiúsculo de `CyberZerk` |

## Conclusão

A lição de awareness: um código 2FA é só uma função determinística de **(segredo, hora)**. Sem celular nenhum, com o segredo em mãos, gera-se qualquer código válido. Quem vaza o segredo (print do QR code, backup do autenticador, banco do servidor) clona o segundo fator — o fator "algo que você tem" é, na prática, "algo que você sabe e guarda bem".

---

## Apêndice — ferramentas

Receita completa (CyberChef, quatro abas/etapas):

1. `JBSWY3DPEHPK3PXP` → `From Base32` → `To Hex` → chave
2. `1762900000 30` → `Divide` → parte inteira → `To Base` (16) → pad a 16 dígitos
3. `000000000380a845` → `From Hex` → `HMAC` (key HEX, SHA1)
4. offset/4 bytes à mão → `From Base` (16) → `MOD` 1000000 → pad a 6 dígitos

Conferência em uma linha:

```bash
oathtool --totp -b JBSWY3DPEHPK3PXP --now=@1762900000
# -> 053377
```
