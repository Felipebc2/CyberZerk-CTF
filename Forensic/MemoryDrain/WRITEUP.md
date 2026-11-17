<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Vidage+de+M%C3%A9moire" alt="Typing SVG" /></a>

</div>

# Vidage de Mémoire — FORENSIC · 🟣 EXTREMO

- **Status:** ✅ RESOLVIDO — struct `AUTHBLK` no heap guarda a chave XOR, o tamanho e o token ofuscado lado a lado
- **Pontos:** 230
- **Anexo / Alvo:** `heap.dump` (20 593 bytes, sem formato, SHA256 `b59883f42002d5b2431eb485797ff865fbf9a8f910c9fe2a91b2a5f1a1ccab85`) + `README.txt`
- **Enunciado:** *"Vidage mémoire du service d'auth RH. Les identifiants n'y sont pas en clair : la structure AUTHBLK conserve le jeton obscurci."* (no README.txt: *"Vidage mémoire du service d'authentification RH (après incident). Les identifiants n'y sont pas en clair : la structure interne 'AUTHBLK' conserve le jeton obscurci."*)
- **Flag:** `CyberZerk{c0r3_dump_struct_x0r_auth_bl0ck}`

---

## TL;DR

1. O `heap.dump` é um recorte do heap de um processo: ruído aleatório com duas estruturas legíveis, `AUTHBLK` e `LOGBUF`.
2. O `AUTHBLK` é uma struct `assinatura | chave | tamanho | reservado | token`. O token está em XOR de 1 byte, e a chave (`0x5a`) fica no próprio cabeçalho.
3. Recortando os 42 bytes do token e aplicando XOR `0x5a`, sai a flag. O base64 em claro do `LOGBUF` é uma isca.

## Análise

### 1. Triagem

```bash
file heap.dump                  # data
strings -n 6 heap.dump          # quase só lixo, mais AUTHBLK e LOGBUF
grep -boa 'AUTHBLK' heap.dump   # 8192:AUTHBLK
grep -boa 'LOGBUF' heap.dump    # 12341:LOGBUF
```

O `file` não reconhece nada, e o arquivo tem 20 KB, pequeno demais para uma imagem de RAM. Por isso o Volatility não se aplica: não há kernel nem tabela de processos, só um pedaço da memória de um processo. A entropia por bloco de 2 KiB fica em cerca de **7,9 bits/byte**, a de bytes aleatórios. O que interessa são os marcadores legíveis no meio desse ruído.

`grep -boa`: `-b` imprime o offset em bytes, `-o` mostra só o trecho encontrado e `-a` trata o binário como texto.

### 2. Ler a struct com `hexdump`

```bash
hexdump -C -s 0x2000 -n 64 heap.dump
```

- `-C`: formato canônico, com offset, bytes em hex e ASCII;
- `-s 0x2000`: pula até o offset 8192, onde o `grep` achou o `AUTHBLK`;
- `-n 64`: mostra só 64 bytes.

```
00002000  41 55 54 48 42 4c 4b 00  5a 2a 00 19 23 38 3f 28  |AUTHBLK.Z*..#8?(|
00002010  00 3f 28 31 21 39 6a 28  69 05 3e 2f 37 2a 05 29  |.?(1!9j(i.>/7*.)|
00002020  2e 28 2f 39 2e 05 22 6a  28 05 3b 2f 2e 32 05 38  |.(/9.."j(.;/.2.8|
00002030  36 6a 39 31 27 01 64 1e  72 d2 21 fb d8 e8 75 ac  |6j91'.d.r.!...u.|
```

Depois da assinatura, os bytes ficam quase todos na faixa estreita `0x20`–`0x3f`. Ruído aleatório se espalha por `00`–`ff`, então isso é texto passado por uma transformação simples. O byte `05` se repete onde um `_` cairia numa flag. Em `0x2036` a faixa volta a ser `00`–`ff` (`d2`, `fb`, `e8`): o dado acabou.

### 3. Delimitar o token pelo cabeçalho

Programas guardam dados como *structs*: campos em ordem fixa, normalmente `[assinatura][cabeçalho][dado]`. Os 4 bytes depois de `AUTHBLK\0` são `5a 2a 00 19`, e `0x2a` = **42**, um valor plausível de tamanho. O último byte antes do ruído é o `27` em `0x2034`. Contando 42 bytes para trás:

```bash
python3 -c "print(hex(0x2034 - 42 + 1))"   # 0x200b
hexdump -C -s 0x200b -n 1 heap.dump        # 19
```

O token vai de `0x200b` a `0x2034`. O `19` é o primeiro byte do dado, não do cabeçalho.

### 4. Recuperar a chave com texto conhecido

No XOR, `cifrado = claro ⊕ chave`, logo `chave = cifrado ⊕ claro`. Toda flag começa com `CyberZerk{`, então o primeiro byte já entrega a chave:

```bash
python3 -c "print(hex(0x19 ^ ord('C')))"   # 0x5a
python3 -c "print(hex(0x5a ^ ord('y')))"   # 0x23 = segundo byte do token ✓
```

A segunda conta vai no sentido inverso: cifra o `y` com a chave candidata e obtém exatamente o byte em `0x200c`. A hipótese de XOR de 1 byte com chave `0x5a` está confirmada. Essa chave é o primeiro campo do cabeçalho, então a struct fica:

| Offset | Bytes | Campo |
|---|---|---|
| `0x2000` | `41 55 54 48 42 4c 4b 00` | assinatura `AUTHBLK\0` |
| `0x2008` | `5a` | chave XOR |
| `0x2009` | `2a` | tamanho do token (42) |
| `0x200a` | `00` | reservado/alinhamento |
| `0x200b`–`0x2034` | `19 23 … 27` | token ofuscado |

### 5. Desofuscar

**CyberChef:** cole os 42 bytes (`19 23 38 … 39 31 27`) e use a receita **From Hex** (Auto), depois **XOR** (Key `5a`, formato HEX).

**Terminal**, lendo direto do arquivo:

```bash
python3 -c "d=open('heap.dump','rb').read()[0x200b:0x200b+42]; print(bytes(b^0x5a for b in d).decode())"
```

`[0x200b:0x200b+42]` é o mesmo recorte do `-s` e `-n` do `hexdump`.

```
CyberZerk{c0r3_dump_struct_x0r_auth_bl0ck}
```

A flag descreve a técnica: *core dump → struct → XOR → auth block*.

### 6. Descartar a isca do `LOGBUF`

```bash
hexdump -C -s 12320 -n 128 heap.dump
```

Em `0x3035` aparece `LOGBUF\0\0` seguido de um base64 **em claro**:

```bash
echo 'Q3liZXJaZXJre2RlY295LWFuYzEzbl9qZXQwbl9kM190M3N0fQ==' | base64 -d
# CyberZerk{decoy-anc13n_jet0n_d3_t3st}
```

É uma isca, com `decoy` escrito no nome: *"ancien jeton de test"*. É o que um `strings | base64 -d` apressado encontraria primeiro. O enunciado já avisava que o token verdadeiro não está em claro.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Tratar como dump de RAM e usar o Volatility | ✗ | 20 KB, sem kernel nem perfil; é um recorte de heap de um processo |
| Copiar o trecho inteiro depois de `AUTHBLK\0` como token | ✗ | Pegava o cabeçalho (`5a 2a 00`) no começo e ruído (`01 64 1e …`) no fim; o tamanho `0x2a` delimita os bytes exatos |
| Usar o tamanho como byte no XOR (`0x42 ^ 'C'` = `0x01`) | ✗ (erro de leitura) | 42 é o número de bytes, não um byte do token; o XOR tem que usar o primeiro byte cifrado (`0x19`) |
| Flag no base64 do `LOGBUF` | ✗ (isca) | Decodifica para `CyberZerk{decoy-…}`; o enunciado diz que o token não está em claro |

## Conclusão

Forense de heap sem ferramenta pronta: achar a assinatura da struct, inferir o layout pelos valores (o tamanho bate com a extensão do dado) e quebrar a ofuscação com texto conhecido. XOR de 1 byte não resiste a um único caractere conhecido, e aqui a chave nem estava escondida: ficava no cabeçalho, ao lado do dado.

Lição defensiva: ofuscação não é criptografia. Segredos em memória devem ficar o mínimo de tempo possível e ser zerados depois do uso (`explicit_bzero`, `SecureZeroMemory`). Se precisarem ser protegidos, a chave deve estar fora do processo (HSM, TPM, keyring do SO). Core dumps de serviços de autenticação devem ser desativados ou tratados como dados sensíveis (`ulimit -c 0`, `fs.suid_dumpable=0`, `systemd-coredump` com `Storage=none`).

---

## Apêndice — ferramentas

- `grep -boa 'MARCA' X`: offset em bytes de uma string num binário.
- `hexdump -C -s <offset> -n <qtd> X`: ler bytes a partir de um offset (o `xxd` não estava instalado).
- `python3 -c "print(hex(a ^ b))"`: XOR de bytes avulsos para testar uma chave.
- `open(X,'rb').read()[ini:ini+n]`: recortar bytes em Python, equivalente a `dd skip=ini count=n`.
- CyberChef: **From Hex** + **XOR** (Key HEX), ou **XOR Brute Force** quando não há texto conhecido.
