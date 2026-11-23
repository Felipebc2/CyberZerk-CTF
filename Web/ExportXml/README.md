<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Export+XML" alt="Typing SVG" /></a>

</div>

<h1 align="center">Export XML — WEB · 🔴 DIFFICILE</h1>

<p align="center">✅ <b>RESOLVIDO</b> · 175 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://export-xml.cyberzerk.fr/"><code>export-xml.cyberzerk.fr</code></a> · <b>Vetor:</b> XXE in-band (<code>file:///flag.txt</code> refletido no campo <code>&lt;agent&gt;</code>)</p>

---

**Enunciado:** *"L'import de demandes de congés accepte du XML (POST). Faites-lui lire un fichier local."*

**Dica do app (INTRANET TRICATEL):** *"HR import module: accepts leave requests in XML format. Note: legacy parser reused from the old HRIS, I haven't touched the options. It works, we'll see later."* → parser legado com entidades externas habilitadas.

**Anexo:** `CONNEXION.txt` (download da plataforma).

**Formato do POST:**

```xml
<request><agent>Name</agent><reason>...</reason></request>
```

O campo `<reason>` é refletido na resposta (`Motif : ...`) → sink de saída para o XXE.
