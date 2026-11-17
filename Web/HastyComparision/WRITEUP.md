<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Hasty+Comparison" alt="Typing SVG" /></a>

</div>

# Hasty Comparison (Comparaison Hâtive) — WEB · 🟡 MÉDIO

- **Status:** ✅ RESOLVIDO — vazamento do backup `config.php.bak` → md5 do PIN admin quebrado por força bruta (6 dígitos)
- **Pontos:** 100
- **Anexo / Alvo:** `https://comparaison-hative.cyberzerk.fr/` (porta 8080; parâmetro `?pin=<code>`) · `CONNEXION.txt`
- **Enunciado:** *"The portal manager checks a PIN code by comparing its md5... a little quickly. `?pin=`. Trouvez un code accepté."*
- **Flag:** `CyberZerk{un3_sauv3g4rd3_.bak_tr4h1t_l3_pin}`

---

## TL;DR

1. Portal de manager protegido por um PIN de **6 dígitos**, validado por `md5($pin)` no servidor. O enunciado ("compara o md5 um pouco rápido demais") e a nota do dev ("PIN admin a 6 chiffres, je l'ai mis en dur") empurram para **type juggling / magic hash** — mas isso é **isca**.
2. O verdadeiro bug está num **comentário HTML** do fonte: `<!-- TODO ... virer la sauvegarde config.php.bak ... elle traine a la racine -->`. O backup `config.php.bak` fica **servido como texto** na raiz (**source disclosure**) e entrega `$PIN_HASH = "1a31076f2aeb1e7d69120c9f85c3a8da"`.
3. PIN de 6 dígitos = só `10^6` possibilidades → **quebra offline** do md5 em menos de 1 s (`pin = 496135`). `?pin=496135` → área de admin + flag.

## Análise

### Recon — o que o reto mostra

A página (`?pin=<code>`, método **GET**) responde sempre `PIN refusé.` para valor errado. A nota do dev no corpo:

```
// Note: PIN admin a 6 chiffres, je l'ai mis en dur. Pas le temps de faire propre, je verrai lundi.
```

Combinada com o enunciado "comparant son md5 **un peu vite**" (= comparação **frouxa** `==`), isso aponta para **PHP type juggling com magic hash**: se o servidor faz `md5($pin) == $hash` e o valor guardado for um *magic hash* (`0e` + 30 dígitos → o `==` do PHP interpreta como `0`), qualquer entrada cujo md5 também seja `0e…` casaria.

### Falsificação da hipótese "magic hash" (o passo que vira a mesa)

Interrogando o oráculo (mesma mensagem `PIN refusé.` em todos):

| Entrada | Tamanho | md5 é magic? | Resposta |
|---|---|---|---|
| `240610708` | 9 | sim (`0e4620…`) | refusé |
| `QNKCDZO` | 7 | sim (`0e8304…`) | refusé |
| `123456` | 6 | não | refusé |
| `aqNm7j` (gerado) | 6 | **sim** (`0e6893…`) | **refusé** |

O último é decisivo: um magic hash **de 6 caracteres**, gerado por força bruta offline, foi **recusado**. Se o servidor fizesse juggling ingênuo contra um valor magic, esse token entraria. Não entrou → **o valor guardado não é magic** (e/ou há filtro de dígitos). Conclusão: **type juggling não é o vetor.** A hipótese "óbvia" era isca.

### Pivô — source disclosure via `.bak`

Lendo o fonte da página (`Ctrl+U`), o vazamento estava num comentário:

```html
<!-- TODO Didier: virer la sauvegarde config.php.bak avant la prod, elle traine a la racine. -->
```

`config.php` é **executado** pelo PHP (você nunca vê o código). Mas `config.php.bak` **não** está mapeado ao interpretador → o servidor o entrega como **arquivo estático de texto**. Acessando `https://comparaison-hative.cyberzerk.fr/config.php.bak`:

```php
<?php
// Configuration portail manager Tricatel.
$PIN_HASH = "1a31076f2aeb1e7d69120c9f85c3a8da"; // md5 du PIN admin (6 chiffres)
```

### Exploração — crack do md5 (segredo fraco)

md5 é **mão única** (não se "reverte"); quebra = força bruta: hashear candidatos e comparar. O que torna trivial aqui **não é fraqueza do md5**, é o **espaço minúsculo**: 6 dígitos = `10^6` candidatos.

```
$ python3 solve.py
[+] ACHOU: pin = 496135  (0.429s, 496,135 tentativas)

# equivalente com john (ataque por máscara):
$ john --format=raw-md5 --mask='?d?d?d?d?d?d' hash.txt
496135  (?)        # ?d = um dígito; seis ?d = PIN de 6 dígitos (10^6)
```

`https://comparaison-hative.cyberzerk.fr/?pin=496135` → `PIN correct. Bienvenue, manager.` + jeton:

```
CyberZerk{un3_sauv3g4rd3_.bak_tr4h1t_l3_pin}
```

(Trocadilho FR: *"une sauvegarde .bak trahit le PIN"* — um backup `.bak` traiu o PIN.)

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Magic hash pronto da `spaze/hashes` (`240610708`, `QNKCDZO`) | ✗ | 7–9 chars; e o valor guardado não é magic — nenhum casa |
| Gerar magic hash **de 6 chars** offline (`aqNm7j`, md5 `0e6893…`) | ✗ | recusado também → prova que o servidor **não** faz juggling ingênuo; vetor é outro |
| Magic hash de **6 dígitos puros** | ✗ (impossível) | varredura `000000–999999`: **nenhum** número de 6 dígitos tem md5 `0e`+dígitos |
| Brute force do PIN **no servidor** (10^6 requests) | ✗ (proibido) | seria scan massivo contra o alvo — regra do CTF; a quebra tem que ser **offline** |

## Conclusão

Reto de **source disclosure** (arquivo de backup `.bak` servido como texto) + **segredo fraco** (PIN de 6 dígitos em md5, quebrável offline). A camada de "comparação md5 apressada" é deliberadamente uma **isca** para type juggling; a solução real é ler o `config.php.bak` esquecido na raiz e inverter o hash por força bruta no espaço minúsculo.

Correções: (1) **nunca** deixar backups (`.bak`, `.old`, `~`, `.swp`) na raiz web — e configurar o servidor para negar essas extensões; (2) PIN de 6 dígitos é entropia baixíssima — md5 (rápido, sem salt) o torna instantâneo de quebrar: usar segredo forte + hash lento com salt (bcrypt/argon2); (3) não confiar em comentários/TODOs no HTML entregue ao cliente. Flag confirmada na plataforma.

---

## Apêndice — ferramentas

- `solve.py` — `python3 solve.py`: percorre `000000–999999`, compara o md5 de cada candidato com `$PIN_HASH` e imprime o PIN (`496135`). Variante anterior do script buscava *magic hash* de 6 chars (hipótese descartada).
- **john / hashcat** — crack por **máscara**: `?d`=dígito, `?l`=minúscula, `?u`=maiúscula, `?s`=símbolo, `?a`=todos, `?h`=hex. `?d?d?d?d?d?d` = 6 dígitos (`10^6`). `john --format=raw-md5 --mask='?d?d?d?d?d?d' hash.txt` / `hashcat -m 0 -a 3 <hash> '?d?d?d?d?d?d'`.
- **Recon** — `Ctrl+U` (view-source) revelou o comentário; `config.php.bak` acessado direto na raiz (source disclosure).
- `CONNEXION.txt` — anexo do reto: `comparaison-hative.cyberzerk.fr (HTTP 8080 ; ?pin=<code>)`.
