<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Delegated+Signature" alt="Typing SVG" /></a>

</div>

<h1 align="center">Delegated Signature — WEB · 🔴 DIFFICILE</h1>

<p align="center">✅ <b>RESOLVIDO</b> · 175 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://signature-deleguee.cyberzerk.fr/"><code>signature-deleguee.cyberzerk.fr</code></a> · <b>Vetor:</b> JWT algorithm confusion <code>RS256 → HS256</code></p>

---

**Enunciado:** *"Tokens are issued in RS256. Endpoints /login /pubkey /admin. Become an administrator."*

**Endpoints:**

| Rota | Função |
|---|---|
| `GET /pubkey` | chave pública (PEM) — exposta "para integrações" |
| `GET /login` | obter um jeton (JWT RS256) |
| `GET /admin` | espaço admin (`Authorization: Bearer ...`) |

**Ideia:** servidor assina RS256 mas (provavelmente) verifica confiando no `alg` do header. Trocar para `HS256` e assinar com o **PEM público como segredo HMAC** → assinatura válida com chave conhecida.
