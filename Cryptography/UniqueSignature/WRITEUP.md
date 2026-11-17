<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Signature+Unique" alt="Typing SVG" /></a>

</div>

# Signature Unique — CRYPTO · 🟣 EXTREME

- **Status:** ✅ RESOLVIDO — **ECDSA nonce reuse** (nonce `k` repetido em duas assinaturas) sobre a curva secp256k1
- **Pontos:** 323 (autor Perceval, 92 solves)
- **Anexos:**
  - `signatures.json` (736 bytes, sha256 `5dac87c7c79a6a501169fc8c61fc0ab56bd227b4a70ed0754e5707538207cc8e`) — curva, chave pública, `msg1/r1/s1`, `msg2/r2/s2`
  - `vault.bin` (48 bytes, sha256 `c80de749a59f1a6e20c7ad1337b30789f7ac0e4d24aa422b435bc127796732f9`) — flag cifrada em AES-256-ECB
  - `README_1.txt` (200 bytes, sha256 `b1c16288a48627c9e15cf96295a4b02acdd6207562f94b11005a6d4bee1e4c4e`)
- **Enunciado:** *"Deux approbations signées ECDSA par le même compte (Didier), avec le même nonce. signatures.json : clé publique + les deux signatures. vault.bin : le flag chiffré (AES-256-ECB, clé = SHA256(str(d)))."*
- **Flag:** `CyberZerk{ECDSA_m3m3_n0nc3_d0nn3_la_cl3_pr1v33}`

---

## TL;DR

1. As duas assinaturas têm **`r1 == r2`**. Em ECDSA o `r` só depende do nonce `k`, então `r` igual ⇒ **mesmo `k` reusado** — o erro fatal do ECDSA.
2. Duas assinaturas com o mesmo `k` dão um sistema linear que **vaza a chave privada `d`** com álgebra simples (dois inversos modulares), sem força bruta.
3. Com `d`, a chave AES é `SHA256(str(d))` → decifra `vault.bin` → flag.

## Análise

### 1. Identificar o nonce reusado

`signatures.json` entrega curva + chave pública + duas assinaturas:

```
courbe = secp256k1
msg1 = "Approbation conge: Marc_V du 02 au 06 decembre"
r1   = 25055596398547889356334729290473449046184699530611664872248825138189355761432
s1   = 49215999468602600991336980585844915858736227362018955672974740293423745345999
msg2 = "Approbation conge: Didier du 09 au 13 decembre"
r2   = 25055596398547889356334729290473449046184699530611664872248825138189355761432   # == r1 !
s2   = 11058228243925922216656496590091745643432958764414637834793136007186969728103
```

`r1 == r2`. Em ECDSA, `r = (k·G).x mod n` — ou seja, `r` é função **só** do nonce `k` (e da curva), **não** da mensagem. Dois `r` idênticos para mensagens diferentes ⇒ o mesmo `k` foi usado nas duas assinaturas. O enunciado ("même nonce") confirma; `r1 == r2` é a prova no dado.

### 2. Por que nonce repetido vaza a chave privada

A assinatura ECDSA de uma mensagem com hash `z` é:

```
s = k⁻¹ · (z + r·d)  mod n
```

onde `d` = chave privada, `k` = nonce (deveria ser aleatório e único), `n` = ordem do grupo. Com **o mesmo `k`** (logo o mesmo `r`) em duas mensagens:

```
s1 = k⁻¹·(z1 + r·d)
s2 = k⁻¹·(z2 + r·d)
```

Subtraindo, o termo `r·d` (e o `k⁻¹`) se combinam e **o `d` some da diferença**, isolando `k`:

```
s1 − s2 = k⁻¹·(z1 − z2)   ⇒   k = (z1 − z2) · (s1 − s2)⁻¹  mod n
```

Recuperado o `k`, volto em qualquer uma das equações e isolo `d`:

```
s1·k = z1 + r·d   ⇒   d = (s1·k − z1) · r⁻¹  mod n
```

Nada de fatorar, nada de brute force — **dois inversos modulares** (`pow(x, -1, n)` nativo do Python 3.8+) e acabou. É por isso que reusar nonce é o pecado mortal do ECDSA (mesmo bug que abriu o console PS3 e carteiras Bitcoin).

> `z` = hash da mensagem como inteiro. A ordem `n` do secp256k1 tem 256 bits e o SHA256 também, então `z = int.from_bytes(sha256(msg), "big")` direto, sem truncar.

### 3. O segundo estágio (trivial com `d`)

O cofre usa a chave privada derivada como chave AES: `key = SHA256(str(d))` (o `str(d)` = o inteiro `d` em decimal, como texto). 32 bytes → AES-256-ECB. Decifra os 48 bytes (3 blocos) de `vault.bin`, remove o padding PKCS7 → flag.

### 4. Forjar e decifrar

```python
import hashlib, json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141  # ordem do secp256k1
sig = json.loads(open("signatures.json").read())
z = lambda m: int.from_bytes(hashlib.sha256(m.encode()).digest(), "big")

k = (z(sig["msg1"]) - z(sig["msg2"])) * pow(sig["s1"] - sig["s2"], -1, n) % n
d = (sig["s1"] * k - z(sig["msg1"])) * pow(sig["r1"], -1, n) % n
key = hashlib.sha256(str(d).encode()).digest()
flag = unpad(AES.new(key, AES.MODE_ECB).decrypt(open("vault.bin","rb").read()), 16)
```

Saída:

```
[.] r1 == r2 ? True  -> nonce k reusado
[+] nonce k  = 98288658578122535202904927794446851093352516525724922411216268038095655703659
[+] chave privada d = 64505419700603233227940674805070558273191274488227063647929329512513361498242
[.] chave AES = SHA256(str(d)) = 480cdc95dc01a9f1ed198a5d8bf40578a85a76c7a2ee07ed0b182b20aef12789
[+] b'CyberZerk{ECDSA_m3m3_n0nc3_d0nn3_la_cl3_pr1v33}'
```

### 5. O recado, em francês

« **ECDSA, même nonce, donne la clé privée** » — ECDSA com o mesmo nonce entrega a chave privada. Didier assinou a aprovação dele e a do Marc_V com o mesmo `k`; isso bastou pra recuperar a chave secreta da conta.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| `pip install pycryptodome` direto no Python do sistema | ✗ (previsto) | Arch é *externally-managed*; resolvido com `python3 -m venv .venv` local |
| Procurar a chave privada "difícil" (log discreto / força bruta) | ✗ desnecessário | O vetor não é quebrar o ECDSA, é o **nonce reusado**: `r1 == r2` é a dica de que basta álgebra linear |

## Conclusão

A segurança do ECDSA depende de **um nonce `k` único e imprevisível por assinatura**. Reusar `k` (ou usar um `k` previsível) transforma duas assinaturas em um sisteminha linear de duas equações que resolve direto para `d` — a chave privada vaza sem nenhum esforço criptográfico. A defesa é **RFC 6979** (nonce determinístico derivado de `HMAC(d, msg)`, único por mensagem) ou um CSPRNG de verdade; nunca reaproveitar `k`. Lição de leitura de desafio: ao ver dois ECDSA e **`r1 == r2`**, o vetor é nonce reuse — a tríade `r igual` + `dois (s, z)` + `n da curva` é a assinatura exata do ataque.

---

## Apêndice — ferramentas

- `solve.py` — `.venv/bin/python solve.py`: lê `signatures.json`, recupera `k` e `d` com dois inversos modulares, decifra `vault.bin` em AES-256-ECB. Imprime progresso ao vivo.
- Python puro: `hashlib` (hash `z` e chave AES) + inverso modular nativo (`pow(x, -1, n)`, Python ≥3.8). `n` do secp256k1 é constante pública hardcoded. `pycryptodome` só pro AES do segundo estágio.
- Em um CTF genérico, a lib `ecdsa` (ou `fastecdsa`) serve pra conferir a chave pública, mas o ataque em si não precisa de lib de curva — é aritmética mod `n`.
- Arsenal ctf-dispatch: nenhuma ficha cobre ECDSA nonce reuse (busca deu só matches fracos). Ensino direto do playbook.
