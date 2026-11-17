<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Extension" alt="Typing SVG" /></a>

</div>

# Extension — CRYPTO · 🔴 DIFFICULT

- **Status:** ✅ RESOLVIDO — **hash length extension attack** sobre MAC de prefixo-secreto `SHA256(secret || message)`
- **Pontos:** 259 (autor Perceval, 85 solves)
- **Anexos:**
  - `token.txt` (164 bytes, sha256 `37a0d2c99690d6260d4ae81f87e661048401cd5ed7c5818fb48db3b5ca156789`) — `message`, `tag`, `longueur_secret=16`, `append_requis=&role=admin`
  - `sha256ext.py` (2337 bytes, sha256 `274557ae206a8c2d9536ed654d98cbb573cd08076b9d4c1c2ab103378e041a7d`) — SHA256 em Python puro **com `extend()` já pronta**
  - `cipher.bin` (64 bytes, sha256 `538d2ee909b059aa8ecc3755ab97fc29966e8f71b1f33671e7538d61faea518b`) — nota cifrada em AES-256-ECB
  - `README.txt` (258 bytes, sha256 `9517f000efafbe2c382774bf250ee364a968c9d3b2103ba7fad7be910a4ef4cf`)
- **Enunciado:** *"Le cookie RH = message + tag, où tag = SHA256(secret || message), secret de 16 octets. Le coffre s'ouvre si vous présentez un tag valide pour message||...||'&role=admin'. cipher.bin est chiffré en AES-256-ECB, clé = ce tag forgé (32 octets bruts du digest)."*
- **Flag:** `CyberZerk{l3ngth_3xt3ns10n_f0rg3_l4_s1gn4tur3_du_c00k13}`

---

## TL;DR

1. O cookie usa `tag = SHA256(secret || message)` — **MAC de prefixo-secreto**, construção clássica e quebrada: vulnerável a **hash length extension**.
2. Um digest SHA256 **é** o estado interno final do Merkle–Damgård. Com o `tag` e o comprimento absorvido, dá pra fingir que o hash "continuou" e anexar `&role=admin` — **forjando um tag válido sem conhecer o secret**.
3. O desafio entrega a arma pronta (`sha256ext.extend()`). O tag forjado (32 bytes) é a chave AES-256-ECB de `cipher.bin` → flag.

## Análise

### 1. Identificar a construção

`token.txt` mostra o cookie:

```
message = user=marc_v&role=stagiaire
tag     = f81761886a0a96024db3864147e1650b7afe8e196eef08ec34182109d5f25670
longueur_secret = 16
append_requis   = &role=admin
```

O tag é `SHA256(secret || message)`. Esse esquema — pôr o secret como **prefixo** e hashear — parece um MAC, mas vaza. O nome do desafio ("Extension") entrega o vetor: **hash length extension**.

### 2. Por que `SHA256(secret || message)` vaza

SHA256 é Merkle–Damgård: processa a mensagem em blocos de 64 bytes, carregando um **estado de 8 palavras de 32 bits** (256 bits). O digest final **é exatamente esse estado** depois do último bloco. Duas consequências:

| Fato | Consequência |
|---|---|
| o digest = estado interno final | quem tem o tag pode **recarregar o estado** e continuar hasheando |
| antes do fim, o SHA256 insere um **padding** (`\x80` + zeros + comprimento em bits) | se eu souber o **comprimento** de `secret\|\|message`, reproduzo esse padding de cola (`glue`) |

Logo, mesmo **sem saber o secret**, consigo calcular:

```
SHA256( secret || message || glue || "&role=admin" )
```

partindo do tag conhecido. O servidor, ao validar o cookie `message || glue || "&role=admin"`, recomputa `SHA256(secret || <esse cookie>)` e cai no **mesmo** valor que forjei. O `glue` vira bytes "lixo" no meio do cookie, mas o `&role=admin` no fim é o que importa (last-one-wins no parse de query string).

### 3. A ferramenta: `extend()` do próprio desafio

Normalmente usaríamos `hashpump` / `hlextend`. Aqui `sha256ext.py` já traz a primitiva:

```python
def extend(tag, orig_len, append):
    h = list(struct.unpack(">8I", tag))          # recarrega o estado a partir do tag
    total = orig_len + len(glue(orig_len))        # bytes ja absorvidos (multiplo de 64)
    data = append + _pad(total + len(append))     # hasheia o append com o padding final correto
    for i in range(0, len(data), 64): h = _compress(h, data[i:i+64])
    return b"".join(struct.pack(">I", x) for x in h)
```

- `unpack(">8I", tag)` → transforma o digest de volta nas 8 palavras do estado interno.
- `total` → quantos bytes o hash original já "comeu" (secret+message+glue), sempre múltiplo de 64, que é onde o estado está consistente.
- comprime os blocos de `append` com o padding final recalculado para o comprimento total.

`orig_len = 16 (secret) + 26 (message) = 42`.

### 4. Forjar o tag e decifrar

```python
from sha256ext import extend, glue
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

tag = bytes.fromhex("f81761886a0a96024db3864147e1650b7afe8e196eef08ec34182109d5f25670")
orig_len = 16 + len(b"user=marc_v&role=stagiaire")     # 42
forged = extend(tag, orig_len, b"&role=admin")          # tag valido p/ o cookie admin
pt = unpad(AES.new(forged, AES.MODE_ECB).decrypt(open("cipher.bin","rb").read()), 16)
```

Saída:

```
[.] orig_len = 16 (secret) + 26 (message) = 42
[.] glue (padding de cola) = b'\x80\x00...\x00\x01P'     # 0x0150 = 336 bits = 42 bytes
[+] tag forjado = f958fa939ff8c0437e5c00447963ba4978f0474e62f065517b92f97d2ec90cd7
[+] b'CyberZerk{l3ngth_3xt3ns10n_f0rg3_l4_s1gn4tur3_du_c00k13}'
```

O `glue` termina em `\x01\x50` = `0x0150` = 336 = 42×8 bits: é o comprimento de `secret||message` que o SHA256 original gravou. Bate com a teoria.

### 5. O recado, em francês

« **length extension forge la signature du cookie** » — a length extension forja a assinatura do cookie. Promoção de `stagiaire` → `admin` sem jamais conhecer o secret.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| `pip install pycryptodome` direto no Python do sistema | ✗ (previsto) | Arch é *externally-managed*; resolvido com `python3 -m venv .venv` local |
| Tratar o `tag` como um MAC seguro | ✗ conceitual | `SHA256(secret\|\|msg)` **não** é MAC: Merkle–Damgård permite estender. HMAC existe exatamente por isso |

## Conclusão

MAC de prefixo-secreto (`hash(secret || message)`) é quebrado por construção: o digest expõe o estado interno do Merkle–Damgård, e qualquer um que o veja pode **anexar** dados e recalcular um tag válido, bastando saber (ou brutar) o comprimento do secret. A defesa é **HMAC** (`HMAC-SHA256`), cujo duplo hashing com chave fecha essa porta — ou um hash resistente a extensão (SHA-3, BLAKE2). Lição de leitura de desafio: ao ver `tag = SHA256(secret || message)` + "forje um tag para `message || ... || X`", o vetor é **hash length extension** — e a tríade `tag conhecido` + `comprimento do secret` + `append requerido` é a assinatura exata do ataque.

---

## Apêndice — ferramentas

- `solve.py` — `.venv/bin/python solve.py`: importa `extend()` de `sha256ext.py`, forja o tag para `&role=admin` e decifra `cipher.bin` em AES-256-ECB. Imprime progresso ao vivo.
- `sha256ext.py` (fornecido) — SHA256 em Python puro com `extend()`/`glue()`. Em um CTF sem esse brinde, `hashpump` (`hashpumpy`) ou `hlextend` fazem o mesmo.
- Dependência: `pycryptodome` (só pro AES-ECB do segundo estágio).
- Arsenal ctf-dispatch: nenhuma ficha cobre hash length extension (busca deu match fraco). `Arsenal/CRYPTO/aes-ecb-byte-at-a-time.md` toca no AES-ECB, mas aqui o ECB é só decifrar com a chave já forjada — não é o vetor.
