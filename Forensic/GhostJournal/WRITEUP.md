<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Ghost+Journal" alt="Typing SVG" /></a>

</div>

# Ghost Journal — FORENSIC · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — linha `id=4` apagada com `DELETE`, recuperada intacta de um freeblock da página da tabela
- **Pontos:** 125
- **Anexo / Alvo:** `pointeuse.sqlite` (SQLite 3, 8 KB, 2 páginas de 4096 bytes, SHA256 `1d755d9e1257c15dabd341c32fef232d2ac20bdc22c848b5000be0c0879031df`) + `README.txt` (enunciado em francês)
- **Enunciado:** *"Extract from the tipster base. A nighttime score has been 'deleted': queries no longer show it. Find him."* (no README.txt, em francês: *"Extrait de la base de la pointeuse (Tricatel). Un pointage nocturne suspect a été 'effacé'. Les requêtes normales ne le montrent plus. Retrouvez-le."*; "pointeuse" é o relógio de ponto e "pointage", o registro de ponto)
- **Flag:** `CyberZerk{sql1t3_d3l3t3_n3_v1d3_pas_l3s_p4g3s}`

---

## TL;DR

1. A tabela `pointages` tem os ids 1, 2, 3 e 5: **o 4 sumiu**. Não há coluna de exclusão lógica, VIEW nem trigger, então foi um `DELETE` real.
2. O `DELETE` do SQLite **não zera os bytes**. A célula vira um *freeblock* e só os seus 4 primeiros bytes são sobrescritos.
3. As colunas são TEXT, então `strings` lê o registro fantasma direto do arquivo: `ADMIN_SYS`, um badge com a flag e o horário `2026-11-03 02:03`.

## Análise

### 1. Abrir o banco em modo somente leitura

```bash
sqlite3 -box 'file:pointeuse.sqlite?mode=ro&immutable=1'
```

Em forense, abre-se sempre em **somente leitura**: `mode=ro` impede escrita, e `immutable=1` impede até a criação de arquivos `-wal` ou `-journal`. Qualquer escrita pode fazer o SQLite reaproveitar o espaço livre e destruir a evidência.

Um tropeço no caminho: rodar o comando na pasta errada (`StrikesCaptured`) deu *"unable to open database file"*. A URI é relativa, e com `mode=ro` o SQLite não cria um banco vazio no lugar. Sem o `ro`, ele teria **criado silenciosamente** um arquivo vazio, e o `.tables` não mostraria nada.

### 2. Testar a hipótese de exclusão lógica (H1)

```sql
.tables     -- pointages
.schema     -- CREATE TABLE pointages(id INTEGER PRIMARY KEY, agent TEXT, badge TEXT, horodatage TEXT);
SELECT * FROM pointages;
```

| id | agent | badge | horodatage |
|---|---|---|---|
| 1 | Marc_V | B-1007 | 2026-11-03 08:59 |
| 2 | Didier | B-1012 | 2026-11-03 09:14 |
| 3 | DRH | B-1001 | 2026-11-03 07:45 |
| 5 | DAF | B-1003 | 2026-11-03 08:30 |

- As aspas em *'effacé'* sugeriam uma exclusão lógica: uma coluna `deleted`, uma VIEW que filtra ou um trigger. **O schema derruba isso**: é uma tabela única, sem nenhum desses mecanismos.
- **A lacuna no `id = 4`** é a marca de um `DELETE` real. Um `INTEGER PRIMARY KEY` é o `rowid` da linha, e as linhas que sobram não são renumeradas.

### 3. O que um `DELETE` faz no arquivo (H2)

O SQLite guarda cada tabela numa árvore B (*B-tree*) feita de páginas. Aqui, a página 1 tem o `sqlite_schema` e a página 2 é uma *table leaf* (tipo `0x0D`) com as linhas. Cada linha é uma **célula**; o cabeçalho da página tem um **vetor de ponteiros** para as células e o início de uma lista encadeada de **freeblocks**.

Num `DELETE`:
1. o ponteiro da célula sai do vetor, e nenhuma consulta a alcança mais;
2. o espaço da célula entra na lista de freeblocks;
3. **os bytes ficam onde estavam**, a menos que `PRAGMA secure_delete` esteja ativo. Só os 4 primeiros bytes são sobrescritos pelo cabeçalho do freeblock (`u16` com o próximo freeblock e `u16` com o tamanho).

`PRAGMA freelist_count` dá 0, ou seja, nenhuma página inteira foi liberada. O lixo está **dentro** da página 2 viva, e por isso o `.recover` (que vasculha páginas livres e órfãs) não é a ferramenta certa aqui.

### 4. Ler o registro fantasma

Como as colunas são TEXT, os valores estão em ASCII no arquivo:

```bash
strings -n 4 pointeuse.sqlite
```

```
SQLite format 3
;tablepointagespointages
CREATE TABLE pointages(id INTEGER PRIMARY KEY, agent TEXT, badge TEXT, horodatage TEXT)
-DAFB-10032026-11-03 08:30
i-ADMIN_SYSCyberZerk{sql1t3_d3l3t3_n3_v1d3_pas_l3s_p4g3s}2026-11-03 02:03
-DRHB-10012026-11-03 07:45!
-DidierB-10122026-11-03 09:14!
-Marc_VB-10072026-11-03 08:59
```

A segunda linha de dados é o registro apagado: agent **`ADMIN_SYS`**, horodatage **`2026-11-03 02:03`** (o ponto noturno) e, no lugar do badge, **a flag**.

### 5. Validar byte a byte (por que o `i-` aparece antes do nome)

Para confirmar que a leitura não era coincidência, examinamos o cabeçalho da página 2 (que começa no offset 4096):

| Campo | Valor |
|---|---|
| Tipo de página | `0x0D` (table leaf) |
| Número de células | 4 (as linhas vivas) |
| Primeiro freeblock | offset 3916 da página |
| Cabeçalho do freeblock | `00 00 00 4e`: não há próximo freeblock (`0x0000`); tamanho de **78 bytes** (`0x004e`) |

Uma célula de *table leaf* é `[tamanho do payload][rowid][record header][valores]`, e o *record header* é `[tamanho do header][serial type de cada coluna]`. Os serial types para TEXT valem `13 + 2×len`:

| Bytes | Significado |
|---|---|
| ~~`4c 04 05 00`~~ | Sobrescritos pelo freeblock: tamanho do payload (76), rowid **4**, tamanho do header (5), tipo da coluna `id` (0 = NULL, porque o `INTEGER PRIMARY KEY` fica no rowid) |
| `1f` | `agent`: 31 = 13 + 2×9, um texto de 9 bytes (`ADMIN_SYS`) |
| `69` (`i`) | `badge`: 105 = 13 + 2×46, um texto de **46 bytes**, exatamente o tamanho da flag |
| `2d` (`-`) | `horodatage`: 45 = 13 + 2×16, um texto de 16 bytes (`2026-11-03 02:03`) |

A conta fecha: 5 bytes de header + 9 + 46 + 16 = 76 bytes de payload. Somando 1 byte de tamanho e 1 de rowid, dá **78 bytes, exatamente o tamanho do freeblock**. O `i-` que o `strings` mostra são os serial types do badge e do horário, e o `-` antes de cada linha viva é o tipo da sua coluna de 16 caracteres. O `1f` não aparece porque não é um caractere imprimível.

A flag descreve a lição: *"SQLite delete ne vide pas les pages"*, o `DELETE` do SQLite não esvazia as páginas.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Exclusão lógica (coluna `deleted`, VIEW ou trigger) | ✗ (falsificada) | O `.schema` mostra uma tabela única, sem nenhum desses mecanismos |
| Abrir o `.sqlite` na pasta `StrikesCaptured` | ✗ (erro de caminho) | A URI é relativa; com `mode=ro` o SQLite não cria arquivo e falha com *"unable to open database file"* |
| `.schema` direto no bash | ✗ | Os *dot-commands* só existem dentro do shell do `sqlite3` |

## Conclusão

Forense de SQLite: o `id` faltando entrega o `DELETE`, e o formato do arquivo garante que a linha continua lá. Ela só sai do vetor de ponteiros e vira um freeblock com os 4 primeiros bytes sobrescritos. Com colunas TEXT, `strings` basta; com valores inteiros (um timestamp Unix, por exemplo), seria preciso procurar o valor empacotado em binário e decodificar o *record header* (método do Arsenal `sqlite-deleted-record-freeblock-carving`).

Lição defensiva: para apagar de verdade, use `PRAGMA secure_delete = ON` ou rode um `VACUUM` depois do `DELETE`, que reescreve o banco sem o espaço livre.

---

## Apêndice — ferramentas

- `sqlite3 -box 'file:X?mode=ro&immutable=1'`: abre sem nenhuma escrita. Dentro dele, `.tables`, `.schema` e `SELECT`.
- `strings -n 4 X`: texto ASCII no arquivo bruto, inclusive em freeblocks.
- `PRAGMA freelist_count` e o offset 36 do cabeçalho do arquivo: páginas inteiras livres (aqui, 0).
- Cabeçalho da página B-tree (offset `page_start + 0..7`, ou `+100` na página 1): tipo, primeiro freeblock, número de células, início da área de conteúdo.
- GUI: DB Browser for SQLite (`sudo pacman -S sqlitebrowser`). Carvers prontos: `undark`, `bring2lite`.
