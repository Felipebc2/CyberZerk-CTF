<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Fragments" alt="Typing SVG" /></a>

</div>

# Fragments — FORENSIC · 🔴 DIFFICULT

- **Status:** ✅ RESOLVIDO — PNG íntegro escondido no meio de bytes aleatórios; a flag fica no chunk `tEXt` do PNG
- **Pontos:** 150
- **Anexo / Alvo:** `secteur.raw` (9 385 bytes, sem formato, SHA256 `45b0dc1539da350eb13a312c7e61c5fe2efcfc36f7af2a94a345589123abb0b0`) + `README.txt`
- **Enunciado:** *"Fragment brut de l'espace non alloué d'un disque, sans table de fichiers. Retrouvez et extrayez ce qui s'y cache."* (no README.txt: *"Fragment brut récupéré sur l'espace non alloué d'un disque Tricatel. Aucune table de fichiers : à vous de retrouver et d'extraire ce qui s'y cache."*)
- **Flag:** `CyberZerk{c4rv1ng_l3_PNG_surv1t_a_l_3ff4c3m3nt}`

---

## TL;DR

1. O `.raw` é uma cópia crua de um trecho do disco. Não tem sistema de arquivos nem tabela, então só dá para achar arquivos pelo conteúdo: *file carving*.
2. No meio do ruído há um PNG completo, do offset 5000 ao 5288.
3. A flag está num chunk de metadados `tEXt` do PNG. Esse chunk é texto puro, então um `strings` já a mostra; o caminho previsto era recortar o PNG com `dd`.

## Análise

### 1. O que é um `.raw`

```bash
file secteur.raw   # data
```

`.raw` não é um formato, é uma cópia **byte a byte** de um pedaço do disco, sem cabeçalho. Por isso o `file` não reconhece nada.

Num disco normal, o sistema de arquivos (FAT, NTFS, ext4) mantém uma tabela que diz onde cada arquivo começa e quantos bytes tem. Quando um arquivo é apagado, só a entrada da tabela some. Os bytes ficam no **espaço não alocado** até serem sobrescritos. O enunciado diz que não há tabela, então não dá para montar o fragmento nem listar arquivos: é preciso procurá-los pelo conteúdo.

### 2. Triagem: ruído e uma assinatura

Medindo a entropia em blocos de 1 KiB, o arquivo inteiro ficou perto de **7,8 bits/byte**, o valor de bytes aleatórios (o máximo é 8). Ou seja, o fragmento é ruído preenchendo o espaço em volta do que interessa.

Quase todo formato começa com uma assinatura fixa (*magic bytes*), e muitos têm um marcador de fim. Procurando as assinaturas comuns, só uma apareceu, com início e fim:

| Offset | Bytes | Significado |
|---|---|---|
| 5000 (`0x1388`) | `89 50 4E 47 0D 0A 1A 0A` | assinatura do PNG |
| 5281 (`0x14a1`) | `IEND` | chunk final do PNG; o arquivo acaba 8 bytes depois, no byte 5288 (4 do nome `IEND` + 4 do CRC) |

O PNG tem 289 bytes. Todos os CRCs dos chunks conferem, então ele está inteiro:

| Chunk | Conteúdo |
|---|---|
| `IHDR` | 64×64, RGB, 8 bits por canal |
| `iTXt` | `Commentaire` = *"Capture interne — ne pas diffuser"* |
| `tEXt` | `flag` = `CyberZerk{c4rv1ng_l3_PNG_surv1t_a_l_3ff4c3m3nt}` |
| `IDAT` | 105 bytes de pixels comprimidos com zlib |
| `IEND` | fim |

### 3. O atalho: `strings`

```bash
strings secteur.raw
```

No meio do lixo aparecem `IHDR`, `iTXtCommentaire`, `tEXtflag`, a flag, `IDAT` e `IEND`. Funciona por causa da estrutura do PNG: os pixels ficam comprimidos no `IDAT` e viram lixo no `strings`, mas os chunks de metadados `tEXt` e `iTXt` guardam texto puro. O `Z` colado no fim da flag na saída é o primeiro byte do CRC do chunk, não faz parte dela.

### 4. O caminho previsto: carving com `dd`

```bash
dd if=secteur.raw of=carved.png bs=1 skip=5000 count=289
file carved.png        # PNG image data, 64 x 64, 8-bit/color RGB
exiftool carved.png    # Commentaire + flag
```

`skip` pula até a assinatura e `count` copia exatamente até o fim do `IEND`. É o que `binwalk -e` e `foremost` fazem por baixo: procurar a assinatura de início e cortar até o marcador de fim (ou até um tamanho máximo, quando o formato não tem marcador).

### 5. Descartar uma flag isca

Uma flag que aparece fácil num desafio "Difficile" merece desconfiança. Por isso conferi:

- ela está num chunk `tEXt` válido (com CRC certo) cuja chave é `flag`, e não num trecho do ruído que por acaso parece texto;
- a imagem é praticamente de uma cor só, então não há outra flag desenhada nos pixels;
- não há nenhuma outra assinatura de arquivo no fragmento.

A flag descreve a técnica: *"carving : le PNG survit à l'effacement"*, o PNG sobrevive ao apagamento.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| `file secteur.raw` identificar o conteúdo | ✗ | `.raw` não tem cabeçalho; o `file` só olha o começo, e o PNG está no offset 5000 |
| "Fragments" significar um arquivo quebrado em pedaços, a remontar | ✗ (não foi o caso) | O PNG estava contíguo e com todos os CRCs válidos |
| A flag de texto ser uma isca | ✗ (descartada) | Chave `flag`, CRC válido, imagem de cor única e nenhum outro arquivo no ruído |

## Conclusão

*File carving*: sem sistema de arquivos, os arquivos são recuperados pelo conteúdo, procurando a assinatura de início e o marcador de fim e recortando o que está entre os dois. Apagar um arquivo só remove a entrada da tabela; os bytes continuam no disco até serem sobrescritos.

Lição defensiva: para eliminar um dado de verdade é preciso sobrescrevê-lo (`shred`, wipe do disco, ou criptografia de disco com descarte da chave). Em SSD, o TRIM e o *wear leveling* tornam a sobrescrita imprevisível, então a criptografia de disco completo é a defesa confiável. Metadados de imagem (`tEXt`, EXIF) também vazam informação e devem ser removidos antes de publicar (`exiftool -all= arquivo`).

---

## Apêndice — ferramentas

- `file`, `hexdump -C X | head` (o `xxd` não estava instalado): identificar e olhar os bytes.
- `strings X`: sequências ASCII; acha metadados em texto puro, não conteúdo comprimido.
- `binwalk X` (lista assinaturas e offsets) / `binwalk -e X` (extrai).
- `foremost -i X -o out/`: carving por assinaturas de início e fim.
- `dd if=X of=Y bs=1 skip=<offset> count=<tamanho>`: carving manual.
- `pngcheck -v Y`, `exiftool Y`: validar os chunks do PNG e ler os metadados.
- Tabela de assinaturas: Gary Kessler, *File Signatures* (garykessler.net/library/file_sigs.html).
