<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Facade+smile" alt="Typing SVG" /></a>

</div>

# Facade smile — STEGANOGRAPHY · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — ZIP colado depois do fim do WebP (arquivo poliglota)
- **Pontos:** 100
- **Anexo:** `motivation.png` (na verdade WebP lossless com alfa, 27533 bytes)
- **Enunciado:** *"HR has just published this motivational poster on the company network to "boost" developers before the big production launch. But the graphic designer, on the brink of collapse, discreetly hid his true feelings there. Look beyond appearances."*
- **Flag:** `CyberZerk{S0ur1r3_P0ur_C4ch3r_L3_Burn0ut}`

---

## TL;DR

1. `file` revela que o "PNG" é um WebP.
2. O cabeçalho RIFF declara 27204 bytes, mas o arquivo tem 27533: há 329 bytes sobrando depois do fim da imagem.
3. Esses bytes são um ZIP com `journal_intime.txt`; `unzip motivation.png` extrai a flag.

## Análise

### 1. O recipiente mente sobre o formato

```
$ file motivation.png
motivation.png: RIFF (little-endian) data, WebP image, lossless, with alpha
```

A extensão `.png` não vale nada: quem define o formato são os primeiros bytes (*magic bytes*). Aqui eles são `RIFF....WEBPVP8L`, um WebP lossless. Isso já mostra que o arquivo foi preparado à mão.

### 2. Bytes depois do fim

Um WebP é um contêiner RIFF: os bytes 4–7 guardam o tamanho do conteúdo (little-endian). O fim real da imagem é esse valor + 8.

| O que | Offset |
|---|---|
| Fim do WebP (tamanho RIFF + 8) | 27204 |
| `PK\x03\x04` (local file header do ZIP) | 27204 |
| Nome `journal_intime.txt` | 27234 |
| `PK\x05\x06` (End of Central Directory) | 27511 |
| Tamanho total do arquivo | 27533 |

O ZIP começa exatamente onde a imagem termina. O nome `journal_intime.txt` também aparece num `strings` simples, e foi assim que ele chamou a atenção.

### 3. Por que funciona (arquivo poliglota)

- **O visualizador de imagem** lê o tamanho do RIFF, decodifica 27204 bytes e ignora o resto. O pôster abre normalmente: é a "fachada".
- **O `unzip`** lê o ZIP **de trás para frente**: procura o End of Central Directory no fim do arquivo, que aponta para o diretório central, que lista os arquivos. O que vem antes do ZIP não atrapalha.

O mesmo arquivo é, ao mesmo tempo, uma imagem válida e um ZIP válido.

```
$ unzip -l motivation.png
warning [motivation.png]:  27204 extra bytes at beginning or within zipfile
  (attempting to process anyway)
  Length      Date    Time    Name
---------  ---------- -----   ----
      161  2026-09-18 22:58   journal_intime.txt

$ unzip -p motivation.png journal_intime.txt
Je n'en peux plus. Ils nous font travailler tous les week-ends sans compensation.
Voici la preuve de mon épuisement : CyberZerk{S0ur1r3_P0ur_C4ch3r_L3_Burn0ut}
```

O aviso de "27204 extra bytes" é o `unzip` dizendo que há 27204 bytes de outra coisa (o WebP) antes do ZIP. É esperado.

A flag fecha o tema: *sourire pour cacher le burn-out*, sorrir para esconder o burn-out.

## O que não funcionou

Nada foi testado e descartado. As hipóteses iniciais, LSB e canal alfa (o WebP é lossless e tem alfa), ficaram na fila: os bytes extras resolveram antes. Um erro meu durante a explicação: antecipei que o aviso do `unzip` falaria em "329 extra bytes" (o tamanho do ZIP), mas o aviso conta os bytes **antes** do ZIP, ou seja, 27204.

## Conclusão

Em stego de imagem, o recon do recipiente vem antes de olhar pixels:

- `file` confere o formato real, sem confiar na extensão.
- Compare o tamanho que o formato declara com o tamanho do arquivo. Se sobrar algo, há dados colados depois do fim.
- `strings` e `binwalk` mostram assinaturas embutidas (`PK` = ZIP).

---

## Apêndice — ferramentas

- `file <arq>`: identifica o formato pelos magic bytes.
- `strings -n 6 <arq>`: mostra textos legíveis, como nomes de arquivo dentro de um ZIP.
- `binwalk <arq>` / `binwalk -e <arq>`: lista e extrai arquivos embutidos.
- `unzip -l <arq>` / `unzip <arq>`: funciona direto no poliglota, porque o ZIP é lido a partir do fim.
- Fim de outros formatos, para comparar: PNG termina no chunk `IEND`, JPEG em `FF D9`, RIFF (WebP/WAV) no tamanho declarado + 8.
