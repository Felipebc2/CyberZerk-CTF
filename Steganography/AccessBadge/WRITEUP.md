<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Access+Badge" alt="Typing SVG" /></a>

</div>

# Access Badge — STEGANOGRAPHY · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — LSB do canal azul escondido numa única linha da imagem
- **Pontos:** 62
- **Anexo:** `badge_marc_v.png` (PNG 480×300, RGB 8 bits)
- **Enunciado:** *"The photo of Marc V.'s badge is circulating on the intranet. The HR department uses it to justify that he "was present". What is this image really hiding?"*
- **Flag:** `CyberZerk{B4dg3_N0cturn3_H3ur3s_C4ch33s}`

---

## TL;DR

1. O anexo é um PNG limpo: sem metadados, sem arquivo anexado, só os chunks IHDR/IDAT/IEND.
2. No **plano de bit 0 do canal azul**, uma única linha (y≈43, logo abaixo do cabeçalho) tem pixels ligados/desligados sem padrão de x=0 até x≈320 e depois fica lisa: payload LSB localizado.
3. O detector do `zsteg` só olha o começo do fluxo de bits, então disse "nothing"; `zsteg -E b1,b,lsb,xy | strings` despeja o fluxo inteiro e a flag aparece.

## Análise

### 1. Triagem do recipiente

| Ferramenta | Resultado |
|---|---|
| `file` | `PNG image data, 480 x 300, 8-bit/color RGB, non-interlaced` |
| `exiftool` | só campos estruturais (sem `Comment`, data, autor) |
| `strings -n 6 \| grep -i cyberzerk` | nada |
| `binwalk` | uma única assinatura PNG de 11908 bytes (= tamanho do arquivo) |
| `pngcheck` (Aperi'Solve) | 3 chunks (IHDR, IDAT, IEND), sem erros |

O `Zlib compressed data` que o `binwalk` do Aperi'Solve aponta em `0x29` é o próprio IDAT (onde todo PNG guarda os pixels comprimidos), não um arquivo escondido. O `Adobe Photoshop Color swatch` que o `zsteg` vê no IHDR é falso positivo: os 13 bytes do IHDR (largura `0x1e0`, altura `0x12c`) passados pelo detector do `file` parecem por acaso o cabeçalho de um swatch.

Conclusão: o dado está **nos pixels**, não no recipiente. PNG é lossless, então LSB sobrevive.

### 2. Por que o `zsteg -a` só devolveu lixo

```
b2,rgb,lsb,yx   .. text: ["U" repeated 10 times]
b3p,r,lsb,yx    .. text: "%%%%%JJJJJJJJJJoooooooooo"
```

O `-equalize` do ImageMagick ([`img/equalize.png`](img/equalize.png)) mostrou que o fundo "liso" do crachá é um **degradê vertical em faixas**: cada faixa tem a mesma cor de ponta a ponta e difere da vizinha em ±1–2 unidades. Lendo em ordem `yx` (coluna a coluna), o `zsteg` encontra dezenas de pixels iguais seguidos, o mesmo bit se repete e vira o mesmo byte (`U` = `0x55` = `01010101`). Sequências como `%%%%JJJJoooo` são o degradê subindo, não uma mensagem.

### 3. Planos de bit

No Decomposer do Aperi'Solve, cada canal tem 8 miniaturas: canto superior esquerdo = **bit 0**, inferior direito = **bit 7** (no bit 7 só sobrevive o texto claro, ≥128). Os bits baixos mostram as listras do degradê, e a barra do rodapé é um bloco liso em todos os 24 planos.

No **Blue, bit 0** ([`img/blue_bit0.png`](img/blue_bit0.png)), há uma fileira logo abaixo do cabeçalho que se comporta diferente de qualquer borda natural:

![Linha y≈43 do Blue bit 0, ampliada 4×](img/blue_bit0_linha43_zoom.png)

- padrão irregular, tipo código de barras;
- começa em x=0 e **para em x≈320**; daí em diante a linha é sólida.

Conta de sanidade: ~320 pixels × 1 bit = 320 bits = **~40 bytes**, tamanho de uma flag `CyberZerk{...}`.

### 4. Extração

O `zsteg` monta o fluxo `b1,b,xy` lendo linha por linha o bit 0 do azul e junta de 8 em 8. A mensagem começa na linha ~43, ou seja, perto do byte 43 × 480 / 8 ≈ 2580 do fluxo. O detector automático só inspeciona o início, por isso o "nothing". Como 480 é múltiplo de 8, uma mensagem que começa em x=0 fica alinhada em bytes, e basta despejar o fluxo inteiro e procurar texto:

```bash
$ zsteg -E b1,b,lsb,xy badge_marc_v.png | strings -n 8
CyberZerk{B4dg3_N0cturn3_H3ur3s_C4ch33s}
```

40 caracteres, exatamente o previsto. A variante `msb` (primeiro bit lido como o mais significativo do byte) não produz texto. A flag fecha com o enunciado: o RH usa a foto para provar presença, e ela esconde as *heures cachées* do badge noturno.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Metadados (`exiftool`) | ✗ | só campos estruturais |
| Flag em texto puro (`strings`) | ✗ | nada (a primeira tentativa travou: faltou o nome do arquivo, `strings` ficou lendo o stdin) |
| Arquivo anexado / embutido (`binwalk`, `foremost`, `pngcheck`) | ✗ | 3 chunks, tamanho bate com o arquivo |
| LSB desde o pixel (0,0) (`zsteg`, `zsteg -a`) | ✗ | só ruído do degradê; o payload não está no começo do fluxo |
| Texto visual de baixo contraste (`-equalize`) | ✗ | revelou só o degradê em faixas, nenhum texto |
| Payload na barra cinza do rodapé | ✗ | bloco liso em todos os 24 planos |
| "Linha suspeita" vista na miniatura | ⚠️ | apontada de forma vaga na miniatura e contestada; só ficou clara ao abrir o plano em resolução nativa e ampliar a faixa y=36–48 |
| `stegsolve` | — | `.jar` não instalado; desnecessário, o `zsteg -E` resolveu |

O painel "Common passwords" do Aperi'Solve listava senhas testadas por outros usuários no OpenStego (`8471`, `nuit`, `était présent`...): ruído de terceiros, não foi usado.

## Conclusão

Fechou porque a inspeção visual dos planos de bit localizou **onde** estava o payload (uma linha só, no canal azul), e isso explicou por que a ferramenta automática falhou. Lição: um "nothing" do `zsteg` não descarta LSB. Ele só descarta LSB **no começo do fluxo**. Quando há uma região suspeita num plano, `zsteg -E <canal> | strings` varre o fluxo inteiro.

---

## Apêndice — ferramentas

- `zsteg -E b1,b,lsb,xy badge_marc_v.png | strings -n 8`: extrai o fluxo do bit 0 do azul e acha a flag.
- `magick badge_marc_v.png -equalize eq.png`: estica o contraste para revelar cores quase iguais.
- [Aperi'Solve](https://www.aperisolve.com/): decomposição em planos de bit (o arquivo do challenge, não o alvo).
- `img/`: `equalize.png` (degradê), `blue_bit0.png` (plano azul bit 0), `blue_bit0_linha43_zoom.png` (faixa y=36–48 ampliada 4×).
