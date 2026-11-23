<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Leave+Balance" alt="Typing SVG" /></a>

</div>

<h1 align="center">Leave Balance — WEB · 🔴 DIFFICILE</h1>

<p align="center">✅ <b>RESOLVIDO</b> · 175 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://solde-conges.cyberzerk.fr/"><code>solde-conges.cyberzerk.fr</code></a> · <b>Vetor:</b> Race condition / TOCTOU em <code>check-then-decrement</code> sem lock</p>

---

**Enunciado:** *"POST /start (balance = 1 day); POST /book consumes; GET /flag. Pass the negative balance."*

**Dica do app (TRICATEL — LEAVE PAY):** *"Management of leave balance. 1 day per account. check then decrement, without lock. It'll be fine, no one clicks twice at the same time. Monday I watch."* → check-then-decrement sem trava = janela TOCTOU.

**Anexo:** `CONNEXION.txt` → `solde-conges.cyberzerk.fr (HTTP 8080 ; POST /start /book, GET /flag)`.

**Endpoints:**

| Rota | Função |
|---|---|
| `POST /start` | loga, zera saldo em 1, seta cookie `sess` (retorna `nonce` + `solde`) |
| `POST /book` | consome 1 dia (check `solde > 0`, depois decrementa — **sem lock**) |
| `GET /flag` | libera a flag se `solde < 0` |

**Ideia:** disparar vários `/book` **em paralelo** na mesma sessão → todos leem `solde = 1` antes de qualquer escrita → decrementos empilham → saldo negativa.
