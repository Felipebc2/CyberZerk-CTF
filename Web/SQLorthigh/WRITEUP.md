<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=SQL+or+thigh" alt="Typing SVG" /></a>

</div>

# SQL or thigh? — WEB (INTRO) · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — bypass de autenticação por SQL injection no login
- **Pontos:** 100
- **Anexo / Alvo:** `https://sql.cyberzerk.fr/` (portal RH em PHP)
- **Enunciado:** *"The main developer of the startup Tricatel-Cyber has just suffered a severe burnout... he coded the authentication system at 4 a.m... The code is sloppy. Log in as an administrator to retrieve the CEO's confidential internal memo and prove the system is faulty."*
- **Flag:** `CyberZerk{SQL_1nj3ct10n_C4us3d_By_Burn0ut}`

---

## TL;DR

1. Login de um portal RH (PHP, seta `PHPSESSID`) cujo backend monta a query concatenando o input entre aspas, sem sanitizar — **SQL Injection**.
2. No campo `USERNAME` envia-se `admin'-- ` (senha qualquer): a aspa fecha a string e o `-- ` comenta o resto da query, incluindo a checagem de senha.
3. O servidor loga como admin e a resposta traz o `MEMO_DIRECTION.TXT` com a flag.

## Análise

### Recon — o login

O alvo é o "TRICATEL CYBER - RH PORTAL", um formulário `USERNAME`/`PASSWORD`. A própria página exibe o comentário do dev:

```
// TODO: Ajouter la vérification CSRF et le hash des mots de passe.
// Note: poussé en prod à 04:12 AM. Trop fatigué, je ferai ça lundi.
```

Ou seja: senha em texto puro e código escrito às pressas. O nome do desafio — **"SQL or thigh?"** — é trocadilho fonético com **SQLi**. A resposta seta `PHPSESSID`, então o backend é PHP.

### Confirmação

O login provavelmente monta algo como:

```php
$query = "SELECT * FROM users WHERE username = '$user' AND password = '$pass'";
```

Enviando só `'` no `USERNAME`, a aplicação devolve uma mensagem **genérica** (`ERR_AUTH: Identifiants incorrects`), não um erro de SQL cru — o app engole o erro. Então a confirmação não é por mensagem de erro, e sim **comportamental**: se um payload de bypass logar como admin, está provado.

### Exploração — auth bypass

No campo `USERNAME` (senha = qualquer coisa, ex. `x`):

```
admin'-- 
```

A query efetiva fica:

```sql
SELECT * FROM users WHERE username = 'admin'-- ' AND password = 'x'
```

- `admin'` fecha a string do username;
- `-- ` inicia um comentário SQL → tudo depois (`' AND password = 'x'`) é ignorado. Isso **remove a checagem de senha** e, de quebra, **limpa a aspa órfã** que sobraria (senão a query ficaria com aspas desbalanceadas → erro de sintaxe).

Resultado: query vira `SELECT * FROM users WHERE username = 'admin'`, o banco retorna a linha do admin e o servidor autentica. A resposta (`ESPACE DIRECTION RH : SESSION AUTHENTIFIÉE`) traz:

```
>> MEMO_DIRECTION.TXT
CyberZerk{SQL_1nj3ct10n_C4us3d_By_Burn0ut}
```

> Nota MySQL: `--` só vira comentário com um espaço depois. Se o campo comer o espaço final, usar `admin'#` (o `#` comenta sem exigir espaço). Caso não se soubesse o nome do usuário admin, `' OR '1'='1' -- ` também funcionaria (torna o `WHERE` sempre verdadeiro e retorna a primeira linha da tabela).

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Teste do `'` esperando erro de SQL na tela | ✗ (inconclusivo) | O app retorna mensagem genérica de "credenciais inválidas"; não vaza o erro de SQL |
| Pista de CSRF do comentário do dev | ✗ (ruído) | CSRF não permite "logar como admin"; o vetor real é SQLi no POST do login |

## Conclusão

Reto INTRO de **SQL Injection / auth bypass**: o backend concatena input do usuário direto na query, sem prepared statements, misturando *comando* e *dado*. A correção correta é usar **consultas parametrizadas** (`PDO`/`mysqli` com placeholders) e hash de senha. Flag obtida e confirmada (`Correct` na plataforma).

---

## Apêndice — ferramentas

- `exploit.sh` — guarda o cURL de recon do alvo (headers do request). A exploração em si foi manual, digitando `admin'-- ` no formulário de login pelo navegador; não exigiu script. Os tokens `cf_clearance`/`PHPSESSID` estão anonimizados como `<TOKEN>`.
- Payloads de bypass: `admin'-- ` · `admin'#` · `' OR '1'='1' -- `
