<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Le+Filtre+Magique" alt="Typing SVG" /></a>

</div>

<h1 align="center">Le Filtre Magique — WEB · 🟣 EXTRÊME</h1>

<p align="center">🟠 <b>PARCIAL</b> · 250 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://filtre-magique.cyberzerk.fr/"><code>filtre-magique.cyberzerk.fr</code></a> (HTTP 8080) · <b>Vetor:</b> traversal-LFI via <code>?page=</code> + escrita por <code>?note=</code> → include executa (RCE provado em repro local, <code>uid=0</code>) · <b>em aberto:</b> localizar o path de escrita do <code>?note=</code></p>

---

**Enunciado:** *"Lecteur de pages d'aide (`?page=`) + bloc-notes (`?note=`). Un filtre maison rejette les wrappers. Obtenez une exécution de commande."*

**Dica do app (TRICATEL — CENTRE D'AIDE):** *"j'ai ajouté un filtre maison contre les wrappers. Bricolé à 2h du mat, ça devrait tenir."* → filtro improvisado = blacklist incompleta.

**Anexo:** `CONNEXION.txt` → `filtre-magique.cyberzerk.fr (HTTP 8080 ; ?page= ?note=)`.

**Estado:**

| Peça | Situação |
|---|---|
| `?page=` → `include()` em `/app/index.php:11`, base `/app/pages/` | ✅ traversal livre, sem `.php`, **leitura arbitrária** |
| Filtro = blacklist de esquemas exatos (`php data expect phar zip glob http`) | ✅ mapeado — libera `file compress.zlib phpinfo ssh2 ftp dict`… |
| Filtro de wrappers | ✅ **decorativo** — prefixo `/app/pages/` mata todo wrapper (confirmado `file://` no alvo) |
| Infra real | ✅ PHP **8.3.36**, `php -S` atrás de **Caddy**, user `player`, `PWD=/app` |
| Race `session.upload_progress` | ✗ **FALSIFICADA** — `php -S` bufferiza o POST → sem janela (independe da versão) |
| `?note=` → `$_SESSION` → `sess_<SID>` | ✗ **FALSIFICADA no alvo** — sessão vazia em todo save_path |
| Controle do nome da nota (18 campos) / spoof de header p/ painel admin | ✗ **FALSIFICADO no alvo** |
| include de arquivo c/ PHP em path conhecido → RCE | ✅ **provado local** (`tw2/` php:8.3 e `magicfilter` php:8.1, `uid=0`) |
| `?note=` como primitivo de escrita | 🟠 **em aberto** — grava arquivo de **nome aleatório / dir desconhecido**; chain write→RCE provado local, falta o nome do campo/dir |

**Próximo (não é probe cego):** abrir o site no **browser** e inspecionar o `<form>` real da nota — os `name=` dos campos entregam o parâmetro que controla o filename (só exercitamos `GET ?note=`). Com o campo certo: traversal no nome → escreve `/app/pages/shell.php` → `?page=shell.php&c=` = RCE. Direções completas no writeup.
