<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=560&height=35&lines=Reprise+de+Session" alt="Typing SVG" /></a>

</div>

<h1 align="center">Reprise de Session — WEB · 🟣 EXTRÊME</h1>

<p align="center">✅ <b>RESOLVIDO</b> · 250 pts · author Perceval · 📖 <a href="WRITEUP.md">Writeup</a></p>

<p align="center"><b>Alvo:</b> <a href="https://reprise-de-session.cyberzerk.fr/"><code>reprise-de-session.cyberzerk.fr</code></a> · <b>Vetor:</b> PHP Object Injection (POP gadget em <code>__wakeup</code>) → leitura arbitrária de arquivo</p>

---

**Enunciado:** *"Les sessions sont des objets PHP sérialisés dans le cookie session. Source fournie. Lisez le flag du serveur."*

**Fonte:** `index.php` com a classe `Template` — o cookie `session` é `base64(serialize(objeto))` e o servidor roda `@unserialize(base64_decode($_COOKIE['session']))`.

```php
class Template {
    public $path = 'templates/welcome.html';
    public $content = '';
    public function __wakeup() { $this->content = @file_get_contents($this->path); }
}
if ($o instanceof Template) { echo $o->content; }
```

**Ideia:** `__wakeup()` roda na desserialização e lê `file_get_contents($path)`, controlado pelo cookie → leitura arbitrária. A flag não é arquivo: é a env var `FLAG=`, lida via `/proc/self/environ`.

**Iscas:** `CyberZerk{decoy-7f0e177bd9ec}` no comentário do `index.php` e a mesma string escondida em zero-width no `README.txt`. A porta `:8080` do `CONNEXION.txt` é interna; usar HTTPS.

**Flag:** `CyberZerk{PHP_uns3r1al1z3_p0p_ch41n_v14_w4k3up}`
