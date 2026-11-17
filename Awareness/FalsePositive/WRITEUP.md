<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=False+Positive" alt="Typing SVG" /></a>

</div>

# False Positive — AWARENESS · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — identificar o mail de phishing pelos headers e decodar seu `X-Tracking-Id` (Base64).
- **Pontos:** — (valor dinâmico; preencher)
- **Anexo:** `boite_reception.txt` (export de uma caixa de entrada, 4 e-mails)
- **Enunciado:** *inbox da Tricatel com 4 mails; a pista avisa que um só não vem mesmo da Tricatel e que "son identifiant de suivi en dit long".*
- **Flag:** `CyberZerk{Un_B0n_R3fl3x3_Un_Cl1c_Ev1t3}`

---

## TL;DR

1. Dos 4 e-mails, 3 são legítimos (`spf/dkim/dmarc = pass`, remetente interno) e 1 é phishing.
2. O phishing (Mail 3) se denuncia nos headers: `spf=fail dkim=none dmarc=fail`, enviado de `srv-ovh-237.cheap-bulk-mail.ru`, assunto de urgência e link `.ru` suspeito.
3. O `X-Tracking-Id` dele é Base64 → decodar devolve a flag. Os outros três decodam `not_phishing_N`, confirmando a triagem.

## Análise

### Triagem dos headers

| Mail | From | SPF/DKIM/DMARC | `X-Tracking-Id` (Base64 →) | Veredito |
|---|---|---|---|---|
| 1 | `paie@tricatel-cyber.fr` | pass/pass/pass | `not_phishing_1` | legítimo |
| 2 | `it-support@tricatel-cyber.fr` | pass/pass/pass | `not_phishing_2` | legítimo |
| **3** | `rh@tricatel-cyber.fr` (via `…cheap-bulk-mail.ru`) | **fail/none/fail** | **a flag** | **phishing** |
| 4 | `newsletter@tricatel-cyber.fr` | pass/pass/pass | `not_phishing_4` | legítimo |

Sinais que fecham o Mail 3 como fraude:

- **Autenticação:** `spf=fail dkim=none dmarc=fail` — os outros três passam nos três.
- **Caminho real:** `Received: from srv-ovh-237.cheap-bulk-mail.ru (45.83.12.207)` em vez do `mx.tricatel-cyber.fr (192.168.10.4)` interno. O display name "DRH Tricatel" é só fachada.
- **Engenharia social:** assunto `URGENT - Vérifiez vos accès sous 24h`, ameaça de suspensão e link ofuscado `http://tricatel-cyber.secure-login[.]ru/verif` (domínio real = `secure-login.ru`, não Tricatel).

### Decodar o tracking id

```
Q3liZXJaZXJre1VuX0Iwbl9SM2ZsM3gzX1VuX0NsMWNfRXYxdDN9  --Base64-->  CyberZerk{Un_B0n_R3fl3x3_Un_Cl1c_Ev1t3}
```

Flag = *"Un bon réflexe, un clic évité"* — a própria lição do challenge.

## Conclusão

Challenge de conscientização sobre phishing: a flag não está escondida por criptografia, e sim atrás da análise correta dos cabeçalhos de autenticação. Confiar no `From` visível seria o "falso positivo" de legitimidade — daí o nome.

---

## Apêndice — comando

```bash
echo 'Q3liZXJaZXJre1VuX0Iwbl9SM2ZsM3gzX1VuX0NsMWNfRXYxdDN9' | base64 -d; echo
# -> CyberZerk{Un_B0n_R3fl3x3_Un_Cl1c_Ev1t3}

# triagem rápida dos 4 tracking ids:
grep X-Tracking-Id boite_reception.txt | awk '{print $2}' | while read b; do echo -n "$b -> "; echo "$b" | base64 -d; echo; done
```
