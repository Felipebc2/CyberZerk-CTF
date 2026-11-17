<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=The+Oracle+of+the+Badge" alt="Typing SVG" /></a>

</div>

# The Oracle of the Badge (L'Oracle du Badge) — CRYPTO · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — decifração ECB **byte a byte** via oráculo de cifragem
- **Pontos:** 174 (autor Perceval, 79 solves)
- **Anexo / Alvo:**
  - `oracle_server.py` (1581 bytes, sha256 `9ca6854f95f1c54472bdf0db668bf75dc17e69a20819a57546f20c02eedb7653`)
  - `CONNEXION.txt` (52 bytes, sha256 `55747c8c75266eb6a26374e0be1e4e6dd3dfd948c85f0afeb49f6b66cf78ba20`)
  - Alvo ao vivo: `<HOST>` = `oracle-badge.cyberzerk.fr` (HTTP, atrás da Cloudflare), `GET /?data=<hex>`
- **Enunciado:** *"The PREFIXE number badge reader || your_entry || SECRET in AES-128-ECB. The service accepts GET /?data= and returns the cipher. Extract the SECRET."*
- **Flag:** `CyberZerk{EcB_r3v3l3_1_0ct3t_a_la_f0is_m3m3_av3c_pr3f1x3}`

---

## TL;DR

1. O serviço cifra `AES-128-ECB( PREFIXE(13B aleatórios) || data || SECRET )` e devolve o hex; nós controlamos `data`.
2. No **ECB**, cada bloco de 16 bytes é cifrado sozinho e de forma determinística → **blocos de texto claro iguais viram blocos cifrados iguais**. Isso permite recuperar o `SECRET` **um byte de cada vez**.
3. Alinhando o prefixo com 3 bytes de enchimento e empurrando o segredo byte a byte contra um "dicionário" de 256 chutes, o `solve.py` extrai a flag em **1429 requisições**.

## Análise

### 1. Ler o código-fonte

`oracle_server.py` entrega tudo:

```python
_KEY    = os.urandom(16)
_PREFIX = os.urandom(13)
_SECRET = os.environ.get("BADGE_FLAG", ...).encode()

def _pad(b):
    n = 16 - (len(b) % 16); return b + bytes([n]) * n      # PKCS#7

def _encrypt(data):
    return AES.new(_KEY, AES.MODE_ECB).encrypt(_pad(_PREFIX + data + _SECRET))
```

Pontos que definem o ataque:

| Fato | Consequência |
|---|---|
| **AES-128-ECB** | bloco de **16 bytes**, sem IV, sem encadeamento |
| chave e prefixo **fixos** enquanto o servidor roda | cifra é **determinística**: mesma entrada → mesma saída |
| `PREFIXE` tem **13 bytes** (tamanho conhecido) | basta **3 bytes** de enchimento para fechar o 1º bloco |
| nós controlamos `data`, colado **antes** do `SECRET` | podemos **empurrar** o segredo para onde quisermos |

### 2. Por que o ECB vaza o segredo

O AES só cifra 16 bytes por vez. O modo ECB é o mais ingênuo: fatia a mensagem em blocos de 16 e cifra **cada um isoladamente**, com a mesma chave e sem ligar um ao outro.

```
claro  → [bloco0][bloco1][bloco2]...
cifra  → [E(bloco0)][E(bloco1)][E(bloco2)]...
```

Logo, **dois blocos de texto claro idênticos produzem dois blocos cifrados idênticos** — e isso é visível "de fora", só comparando o hex. É a brecha que transforma "adivinhar o segredo" em "adivinhar 1 byte".

### 3. Alinhar o prefixo

O texto claro real é `PREFIXE(13) || data || SECRET`. Se eu começar o meu `data` com **3 bytes** quaisquer (`FILL = (16 − 13) mod 16 = 3`), o 1º bloco fica `PREFIXE(13) + 3 bytes meus` = 16 bytes cheios. A partir do **bloco 1** (offset 16), tudo é conteúdo que eu controlo, numa fronteira limpa. Dali em diante é o ataque clássico "byte-at-a-time", só ignorando o 1º bloco (o do prefixo).

### 4. Byte a byte com dicionário

Para descobrir o byte `i` do segredo (já conhecendo `SECRET[0..i-1]`):

1. **Empurrar:** mando uma almofada de `A`s de tamanho `15 − (i mod 16)`, de modo que `SECRET[i]` caia exatamente na **última posição de um bloco**. Guardo esse bloco cifrado como **alvo**.
2. **Dicionário:** mando `almofada || SECRET[0..i-1] || chute`, variando `chute` por todos os 256 valores. Quando o bloco cifrado **bate** com o alvo, o `chute` É `SECRET[i]`.
3. Repito deslizando. Começar os chutes pelos caracteres comuns de flag (minúsculas, dígitos, `_`) corta muito o número de tentativas.

A fronteira de bloco do byte `i` é a mesma nos dois casos porque `almofada + i ≡ 15 (mod 16)` por construção — por isso o bloco-alvo e o bloco do chute coincidem.

### 5. Validação offline antes de tocar o alvo

Como o ataque é adaptativo e custa centenas de requisições, **desenvolvi e validei tudo offline**. O sandbox bloqueia abrir uma porta de escuta, então em vez de subir o servidor HTTP, instanciei o **mesmo** oráculo em memória (AES-ECB, prefixo de 13 bytes, PKCS#7) com um segredo **conhecido** e alimentei a função `recover()` do `solve.py`:

```
[OFFLINE] esperado : CyberZerk{t3st3_l0cal_ecb_byte_a_byte!!}
[OFFLINE] recuperado: CyberZerk{t3st3_l0cal_ecb_byte_a_byte!!}
[OFFLINE] MATCH: True
```

Com o miolo provado (recuperou o segredo exato byte a byte), apontei o **mesmo** `recover()` para o oráculo HTTP real, trocando só o transporte.

### 6. Execução ao vivo

```bash
python3 solve.py 'https://oracle-badge.cyberzerk.fr/' "$cookie"   # cookie = valor do cf_clearance
```

```
[*] CyberZerk{EcB_r3v3l3_1_0ct3t_a_la_f0is_m3m3_av3c_pr3f1x3}
[+] SECRET = CyberZerk{EcB_r3v3l3_1_0ct3t_a_la_f0is_m3m3_av3c_pr3f1x3}
[+] requisicoes ao oraculo: 1429
```

Em francês: « **ECB révèle 1 octet à la fois, même avec préfixe** » — "ECB revela 1 byte por vez, mesmo com prefixo".

## O que não funcionou

| Hipótese / tentativa | Resultado | Por quê |
|---|---|---|
| Confirmar ECB pela resposta ao vivo com 32 bytes `A` (`data=4141...`) | ✗ sem dois blocos de 32-hex iguais | Com prefixo de 13, 32 `A`s só preenchem **um** bloco 100% `A` (offset 16–31); para ver **dois** blocos idênticos eram precisos ≥ 35 `A`s. Não era falha — e o código-fonte já confirmava o ECB |
| Subir o `oracle_server.py` local para atacar via HTTP | ✗ processo morre na hora (exit 144, sem saída) | O sandbox mata quem tenta **escutar** numa porta. Pivot: instanciar o oráculo **em memória** e validar a lógica sem rede |
| `python3 solve.py ... 'cf_clearance=$cookie'` | ✗ travou e foi interrompido | Aspas simples **não** expandem `$cookie`, e ainda passei o prefixo `cf_clearance=` junto; o script quer **só o valor**. Correto: aspas duplas `"$cookie"` |

## Conclusão

ECB é determinístico e cifra cada bloco de 16 bytes isoladamente. Um serviço que cifra `algo_que_eu_controlo || SEGREDO` com ECB e devolve o resultado é um **oráculo**: alinhando o segredo na fronteira de um bloco, cada byte desconhecido vira uma busca entre 256 — e um prefixo de tamanho fixo **não** atrapalha, só exige alguns bytes de enchimento para alinhar. A defesa não é "esconder" o prefixo, e sim **não usar ECB**: um modo com IV/nonce e autenticação (AES-GCM) torna cada cifragem diferente e não vaza igualdade de blocos. Lição prática: quando um serviço cifra "entrada do atacante + segredo" e devolve a cifra, pense **oráculo byte-a-byte** antes de qualquer coisa — e valide o ataque **offline** (aqui, oráculo em memória com segredo conhecido) antes de gastar milhares de requisições no alvo.

---

## Apêndice — ferramentas

- `solve.py` — `python3 solve.py <BASE_URL> [cf_clearance]`: decifração ECB byte a byte. O miolo `recover(enc)` é agnóstico ao transporte (foi validado com um oráculo em memória e depois com o HTTP real). Imprime a flag crescendo ao vivo e o total de requisições.
- Arsenal ctf-dispatch: `Arsenal/CRYPTO/aes-ecb-byte-at-a-time.md` — *"AES-ECB: detection + byte-at-a-time decrypt via oracle"*.
