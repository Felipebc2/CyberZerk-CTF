<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=The+Session+Token" alt="Typing SVG" /></a>

</div>

# The Session Token (Le jeton de session) — CRYPTO · 🔴 DIFFICULT

- **Status:** ✅ RESOLVIDO — recuperação do estado do **MT19937** a partir de 624 saídas e previsão dos tokens seguintes
- **Pontos:** 221 (autor Perceval, 87 solves)
- **Anexos:**
  - `tokens.txt` (6685 bytes, sha256 `a4ac1ddc2b012da7e5d51f5841bd51c528382212979701d6fd01da0e7675c1cb`) — 624 jetons consecutivos (um inteiro de 32 bits por linha)
  - `secret.bin` (53 bytes, sha256 `3e44c24cfb47cc7f7e9c2013aa5ecf3f9d65b9998eb037d21f81dd4104e0276f`) — nota do DRH cifrada
  - `README.txt` (203 bytes, sha256 `c68e66fb0a24f12024d500cd79cb8911d91d5479d44e51d7b02054e5b39089f8`)
- **Enunciado:** *"Le portail RH génère chaque jeton de session via `getrandbits(32)`. tokens.txt : 624 jetons consécutifs interceptés. secret.bin : la note du DRH, chiffrée par XOR avec les octets des jetons SUIVANTS."*
- **Flag:** `CyberZerk{MT19937_s3_cl0n3_av3c_624_s0rt13s_untemper}`

---

## TL;DR

1. `getrandbits(32)` do Python é o **Mersenne Twister (MT19937)** — PRNG determinístico e **não-criptográfico**. O estado interno são **624 palavras de 32 bits**.
2. **624 saídas consecutivas de 32 bits = um estado interno inteiro.** Revertendo o *tempering* de cada saída, reconstrói-se o estado e **prevê-se todo token futuro** — sem seed, sem brute force.
3. O `solve.py` usa `randcrack`: alimenta as 624 saídas, prevê os ~14 tokens **seguintes**, converte em bytes e faz **XOR** com `secret.bin`. Big-endian → nota em claro.

## Análise

### 1. Identificar o PRNG

O enunciado entrega o gerador de bandeja: `getrandbits(32)`. Em Python, o `random` padrão **é** o MT19937. Dois fatos selam o desafio:

| Fato | Consequência |
|---|---|
| MT19937 é **determinístico** | dado o estado, toda saída futura é fixa |
| estado = **624 × 32 bits** | 624 saídas seguidas carregam informação suficiente pra recuperar o estado inteiro |

E o enunciado vaza **exatamente 624** jetons consecutivos. Não é coincidência — é o número mágico do MT19937.

### 2. Por que 624 saídas quebram o MT19937

O MT19937 guarda um vetor de estado de **624 inteiros de 32 bits**. A cada chamada ele produz uma saída aplicando uma função de **tempering** (uma sequência de shifts, ANDs e XORs) a uma palavra do estado:

```
y = state[i]
y ^= (y >> 11)
y ^= (y << 7)  & 0x9D2C5680
y ^= (y << 15) & 0xEFC60000
y ^= (y >> 18)
output = y
```

O ponto fraco: **essa função de tempering é totalmente reversível** (bijetora em 32 bits). Dada uma saída, dá pra recuperar a palavra de estado que a gerou — é o *untempering*. Com 624 saídas consecutivas, reverte-se cada uma e obtém-se as 624 palavras do estado → **o gerador foi clonado**. A partir daí, prever as saídas seguintes é só rodar o MT19937 adiante. Nenhuma criptografia: é cópia de estado.

### 3. A ferramenta: `randcrack`

`randcrack` faz exatamente o *untempering* + reconstrução de estado. A API é mínima:

```python
from randcrack import RandCrack
rc = RandCrack()
for t in tokens:          # exatamente 624 saidas de 32 bits
    rc.submit(t)
nxt = rc.predict_getrandbits(32)   # tokens SEGUINTES, identicos aos do portal
```

Instalação (Arch é externally-managed → venv descartável):

```bash
python3 -m venv .venv && .venv/bin/pip install -q randcrack && .venv/bin/python solve.py
```

### 4. Reconstruir o keystream e decifrar

`secret.bin` tem 53 bytes. Cada token são 4 bytes, então preciso de `ceil(53/4) = 14` tokens seguintes (56 bytes). O keystream são os bytes desses tokens; a **única** dúvida era a ordem dos bytes de cada inteiro (big vs little endian). Testei os dois:

```python
n_next = -(-len(secret) // 4)                       # ceil
nxt = [rc.predict_getrandbits(32) for _ in range(n_next)]
for order in ("big", "little"):
    ks = b"".join(t.to_bytes(4, order) for t in nxt)[:len(secret)]
    out = bytes(a ^ b for a, b in zip(secret, ks))
    print(order, out)
```

```
[+] estado do MT19937 reconstruido
[+] 14 tokens seguintes previstos: [2331280345, 747995014, 4247548241]...
[   big] 'CyberZerk{MT19937_s3_cl0n3_av3c_624_s0rt13s_untemper}' <-- LEGIVEL
[little] b'\x10\x0e\x156\xd8...'   (lixo)
```

**Big-endian** entrega a flag direto.

### 5. O recado, em francês

« **MT19937 se clone avec 624 sorties + untemper** » — "o MT19937 se clona com 624 saídas + untemper". O nome da flag é o próprio diagnóstico: PRNG previsível não serve pra token de sessão.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| `pip install randcrack` direto no Python do sistema | ✗ (previsto) | Arch é *externally-managed*; `pip` global recusa. Resolvido com `python3 -m venv .venv` local |
| XOR com os tokens em **little-endian** | ✗ saiu lixo | O portal serializa os tokens em **big-endian**. Testar os dois no mesmo script evitou adivinhação |

## Conclusão

`random.getrandbits()` (MT19937) **nunca** deve gerar tokens de sessão, nonces ou qualquer segredo: basta observar **624 saídas consecutivas** pra clonar o gerador e prever tudo que vier depois — exatamente o cenário do desafio, onde os tokens "seguintes" viram o keystream do XOR. A defesa é usar um CSPRNG (`secrets` / `os.urandom`), cujo estado não se reconstrói a partir da saída. Lição de leitura de desafio: ao ver `getrandbits`/`random` + "N saídas vazadas", o número **624** é a assinatura do ataque de recuperação de estado do MT19937 — e `randcrack` resolve em segundos.

---

## Apêndice — ferramentas

- `solve.py` — `.venv/bin/python solve.py`: alimenta 624 saídas no `randcrack`, prevê os tokens seguintes e faz XOR com `secret.bin` testando os dois endianness. Imprime progresso ao vivo.
- `randcrack` (PyPI) — faz o *untempering* do MT19937 e a reconstrução de estado por baixo.
- Arsenal ctf-dispatch: `Arsenal/CRYPTO/predictable-seeded-prng-replay.md` (tag `mersenne-twister`, PRNG previsível/replay). O vetor exato — recuperação de estado por 624 saídas — é o caso forte que a ficha menciona.
