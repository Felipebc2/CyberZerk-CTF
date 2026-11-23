<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=560&height=35&lines=Formulaire+en+Double" alt="Typing SVG" /></a>

</div>

<h1 align="center">Formulaire en Double — WEB · 🔴 DIFFICILE</h1>

<p align="center">✅ <b>RESOLVIDO</b> · 200 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://formulaire-en-double.cyberzerk.fr/"><code>formulaire-en-double.cyberzerk.fr</code></a> · <b>Vetor:</b> Second-order SQL injection (SQLite) via <code>username</code> relido no status</p>

---

**Enunciado:** *"Inscription puis consultation de statut. `?action=register&username=...` puis `?action=status&id=N`."*

**Dica do app (TRICATEL — PORTAIL RH):** *"le nom est inséré proprement (PDO). La page statut le relit pour afficher le rôle. Rien à craindre... je crois."* → o insert é seguro (prepared statement), mas a **releitura** no status concatena o nome numa 2ª query = janela second-order.

**Anexo:** `CONNEXION (1).txt` → `formulaire-en-double.cyberzerk.fr (HTTP 8080)`.

**Endpoints:**

| Rota | Função |
|---|---|
| `GET /?action=register&username=…` | grava o nome (PDO) e devolve `id` + `token` por registro |
| `GET /?action=status&id=N&t=TOKEN` | **relê** o nome e monta `SELECT … WHERE name='<nome>'` — exibe `Rôle:` |

**Ideia:** registrar um `username` com payload SQL. Ele dorme gravado (PDO não executa), e **acorda** na releitura do status, onde é concatenado → `UNION SELECT` de 1 coluna extrai a flag de `secrets(flag)`.
