<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Trombinoscope" alt="Typing SVG" /></a>

</div>

# Trombinoscope — STEGANOGRAPHY · 🟡 MÉDIO

- **Status:** ✅ RESOLVIDO — flag no campo EXIF `User Comment`
- **Pontos:** 87
- **Anexo:** `trombi_marc_v.jpg` (JPEG baseline 400×300, 20 kB)
- **Enunciado:** *"The photo of Marc V. on the RH trombinoscope looks banal. But a photo is never just an image: look at what it carries with it."*
- **Flag:** `CyberZerk{M3t4d0nn33s_EXIF_B4v4rd3s}`

---

## TL;DR

1. "O que a foto carrega com ela" = o **recipiente**, não os pixels → metadados.
2. `exiftool trombi_marc_v.jpg` mostra a flag no campo `User Comment`.

## Análise

### 1. Leitura do enunciado

"Uma foto nunca é só uma imagem: veja o que ela **carrega junto**." Um JPEG leva, além dos pixels comprimidos, segmentos de metadados (APP1/EXIF, XMP, comentário `COM`) e pode ter bytes colados depois do marcador de fim `FF D9`. As duas hipóteses apontam para o recipiente.

Como é JPEG, LSB fica praticamente descartado: a compressão DCT reescreve os bits baixos, ao contrário do PNG do [Access Badge](../AccessBadge/WRITEUP.md).

### 2. Metadados

```
$ file trombi_marc_v.jpg
JPEG image data, Exif standard: [TIFF image data, big-endian, direntries=3,
description=Trombinoscope Tricatel - Marc V.], baseline, precision 8, 400x300

$ exiftool trombi_marc_v.jpg
Image Description               : Trombinoscope Tricatel - Marc V.
Artist                          : Service RH
User Comment                    : CyberZerk{M3t4d0nn33s_EXIF_B4v4rd3s}
```

O `file` já denunciava um bloco EXIF com só 3 entradas. Uma foto de câmera real teria dezenas (modelo, exposição, data, GPS...). As três entradas foram escritas à mão: descrição, autor ("Service RH") e o `User Comment` com a flag.

A flag fecha com o tema: *métadonnées bavardes*, metadados tagarelas.

## O que não funcionou

Nada a registrar: a primeira hipótese (metadados) resolveu. Na fila estavam `binwalk` (dados após `FF D9`) e `steghide extract` (senha vazia ou a matrícula `TC-8471` do crachá).

## Conclusão

Em stego de imagem, o primeiro passo é sempre o recipiente: `file` + `exiftool` antes de qualquer análise de pixel. Um EXIF com poucas entradas, sem dados de câmera, é sinal de metadado plantado.

---

## Apêndice — ferramentas

- `exiftool <img>`: lista todos os metadados (EXIF, XMP, IPTC, comentários).
- `file <img>`: resumo rápido do EXIF (número de entradas, descrição).
- Próximos passos se não estivesse lá: `binwalk <img>` (arquivos embutidos ou colados) e `steghide extract -sf <img>` (payload com senha em JPEG).
