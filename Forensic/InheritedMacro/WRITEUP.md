<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Inherited+Macro" alt="Typing SVG" /></a>

</div>

# Inherited Macro — FORENSIC · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — cadeia de ofuscação `Chr()` → base64 → `StrReverse` desfeita estaticamente, sem executar a macro
- **Pontos:** 125
- **Anexo / Alvo:** `macro.vba` (código VBA em texto, UTF-8, 19 linhas, 1 367 bytes, SHA256 `13a19982313be935ca336908be4f518891c5b9501e59377affb160eadcbd3d51`) + `README.txt` (enunciado em francês)
- **Enunciado:** *"Macro taken from the suspicious HR manager's binder. What does it reveal when opened?"* (no README.txt: *"Macro extraite du classeur suspect du DRH. Que révèle-t-elle à l'ouverture ?"*; "classeur" é a pasta de trabalho do Excel)
- **Flag:** `CyberZerk{vba_d3s0bfusc4t10n_ch4in3_chr_b64_r3v3rs3}`

---

## TL;DR

1. `Workbook_Open()` roda sozinho quando a planilha abre e mostra um `MsgBox` com `StrReverse(DecodeBase64(s))`.
2. `s` é montada com 72 chamadas `Chr(n)`, para que o texto não apareça em claro no arquivo.
3. Refazendo os três estágios no shell (ou no CyberChef), sem executar nada, sai a flag.

## Análise

### 1. Ler antes de rodar

A primeira pergunta foi "como rodo essa macro?". Em forense de maldoc, a resposta é **não rodar, emular**. A macro poderia ser maliciosa (dropper, download, persistência), e só dá para saber isso depois de ler. No Linux, rodar nem funcionaria: o LibreOffice até executa VBA, mas o `CreateObject("MSXML2.DOMDocument.3.0")` é um objeto COM que só existe no Windows, e a macro quebraria na decodificação. A ficha do Arsenal `FOR/office-maldoc-vba-static-extraction` segue a mesma regra.

O anexo já é o `.vba` em texto, então não foi preciso extraí-lo de um `.xlsm` com `olevba`. Basta ler:

```vb
Private Sub Workbook_Open()
    Dim s As String
    s = Chr(102) & Chr(84) & Chr(78) & ... & Chr(61) & Chr(61)
    ' s contient une chaîne encodée ; decodee puis inversee a l'execution
    Dim raw As String
    raw = DecodeBase64(s)
    MsgBox StrReverse(raw)
End Sub

Private Function DecodeBase64(ByVal b64 As String) As String
    Dim xml As Object, node As Object
    Set xml = CreateObject("MSXML2.DOMDocument.3.0")
    Set node = xml.createElement("b64")
    node.DataType = "bin.base64"
    node.Text = b64
    DecodeBase64 = StrConv(node.nodeTypedValue, vbUnicode)
End Function
```

| Trecho | O que faz |
|---|---|
| `Workbook_Open()` | Gatilho de execução automática quando a planilha abre (equivale ao `AutoOpen`/`Document_Open` do Word) |
| `Chr(102) & Chr(84) & ...` | Monta a string caractere a caractere a partir dos códigos ASCII, uma ofuscação clássica contra `strings`, grep e assinaturas de antivírus |
| `DecodeBase64` | Decodifica base64 com um truque comum em maldoc: um nó XML do MSXML com `DataType = "bin.base64"` devolve os bytes em `nodeTypedValue` |
| `StrReverse` + `MsgBox` | Inverte o texto e mostra numa caixa de diálogo. É isso que a macro "revela à abertura" |

### 2. Por que o `strings` não basta

O `strings macro.vba` mostra só o **código-fonte**. A flag não existe pronta em lugar nenhum do arquivo: ela só se forma em tempo de execução, depois dos três estágios. Ainda assim, o `strings` deu duas pistas:

- a cadeia termina em `Chr(61) & Chr(61)`, ou seja, `==`, o padding de base64. Isso confirma a hipótese do estágio 2;
- os comentários saem quebrados (`' Macro h` / `e du classeur...`) porque o `strings` só imprime sequências ASCII, e o `é` em UTF-8 (2 bytes fora da faixa ASCII) interrompe a sequência. É um efeito da ferramenta, não uma pista.

### 3. Estágio 1: `Chr(n)` → texto

```bash
grep -oP 'Chr\(\K\d+' macro.vba | awk '{printf "%c", $1}'; echo
```

O `\K` descarta o `Chr(` da saída e deixa só o número; o `printf "%c"` do awk converte cada código no seu caractere. São 72 `Chr` e 72 caracteres:

```
fTNzcjN2M3JfNDZiX3JoY18zbmk0aGNfbjAxdDRjc3VmYjBzM2RfYWJ2e2tyZVpyZWJ5Qw==
```

### 4. Estágios 2 e 3: base64 e inversão

```bash
... | base64 -d          # }3sr3v3r_46b_rhc_3ni4hc_n01t4csufb0s3d_abv{kreZrebyC
... | base64 -d | rev    # CyberZerk{vba_d3s0bfusc4t10n_ch4in3_chr_b64_r3v3rs3}
```

O resultado do base64 já tem cara de flag, só que de trás para a frente (`}...{kreZrebyC`). O `rev` faz o papel do `StrReverse`. A resolução final foi feita no CyberChef com a receita **From Base64 → Reverse (By Character)**.

Um detalhe da receita: o alfabeto selecionado no CyberChef era o URL-safe (`A-Za-z0-9-_`), e mesmo assim funcionou, porque essa string base64 não tem nenhum `+` nem `/`, os dois únicos caracteres em que os alfabetos padrão e URL-safe diferem.

A flag descreve a técnica: *"VBA désobfuscation, chaîne Chr → b64 → reverse"*.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Executar a macro para ver o `MsgBox` | ✗ (descartada) | É um risco em maldoc, e no Linux o `CreateObject("MSXML2...")` (COM do Windows) quebraria a decodificação. Emular os estágios é mais seguro e mais rápido |
| `strings macro.vba` para achar a flag | ✗ | Mostra só o fonte; a flag só se forma em tempo de execução |
| Saída do base64 como flag final | ✗ (invertida) | Faltava o estágio 3, o `StrReverse`, que `rev` ou o Reverse do CyberChef resolvem |

## Conclusão

Análise estática de macro: identificar o gatilho de autoexecução (`Workbook_Open`), mapear cada estágio de ofuscação e reproduzi-lo fora do Office. A ordem importa: o código monta, decodifica e inverte, e a emulação desfaz na mesma sequência.

Lição defensiva: `Chr()` concatenado, base64 via MSXML e `StrReverse` são indicadores clássicos de maldoc. O `olevba` sinaliza todos eles como *suspicious keywords*. Em produção, bloquear macros vindas da internet (Mark of the Web) corta esse vetor.

---

## Apêndice — ferramentas

- `grep -oP 'Chr\(\K\d+' macro.vba | awk '{printf "%c", $1}' | base64 -d | rev`: os três estágios num único pipeline.
- CyberChef: *From Base64* → *Reverse (By Character)*.
- `olevba --decode arquivo.xlsm` (`pipx install oletools`): extrai e decodifica macros de documentos Office sem executar nada; não foi necessário aqui porque o anexo já era o `.vba`.
- ViperMonkey (`vmonkey`): emulador de VBA, para macros grandes demais para desofuscar à mão.
