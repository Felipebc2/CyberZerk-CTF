<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Ghost+Timekeeper" alt="Typing SVG" /></a>

</div>

# Ghost Timekeeper — WEB (INTRO) · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — cookie de identidade forjável (base64 sem assinatura)
- **Pontos:** 50
- **Anexo / Alvo:** `https://pointeuse.cyberzerk.fr/`
- **Enunciado:** *"Tricatel's new timekeeping software discreetly 'forgets' overtime. You only have access to your file. However, someone has the right to see the real hours of the entire team..."*
- **Flag:** `CyberZerk{P0int3us3_Qu1_0ubl13_L3s_H3ur3s_Sup}`

---

## TL;DR

1. O relógio de ponto mostra as horas de um `employee` (#8472); o rodapé diz que só um perfil `manager` vê o registro real do time.
2. A identidade vem num cookie `profil` que é só **base64 de um JSON em texto puro, sem assinatura** → **Broken Access Control**.
3. Decodifica, troca `"role":"employe"` por `"role":"manager"`, re-codifica, reenvia o request → a resposta traz o registro completo com a flag.

## Análise

### Recon — o cookie `profil`

A página (perfil `employee`) traz um aviso: *"Only a manager profile can view the actual register."* Inspecionando os cookies da request, além do `cf_clearance` (Cloudflare, só anti-bot) há um cookie `profil`:

```
profil=eyJlbXBsb3llIjoiVm91cyAoIzg0NzIpIiwicm9sZSI6ImVtcGxveWUifQ%3D%3D
```

### Decodificação

`%3D%3D` é o `==` URL-encodado (padding base64). URL Decode → From Base64:

```json
{"employe":"Vous (#8472)","role":"employe"}
```

O servidor confia num campo `role` que **vive dentro do cookie, controlado pelo cliente** e sem nenhuma assinatura/HMAC. Clássico authz split.

### Forja

Troca `employe` → `manager` e re-codifica (To Base64 → URL Encode):

```
{"employe":"Vous (#8472)","role":"manager"}
→ eyJlbXBsb3llIjoiVm91cyAoIzg0NzIpIiwicm9sZSI6Im1hbmFnZXIifQ%3D%3D
```

### Exploração

Reenvia o `GET /` com o cookie `profil` forjado (mesmo `cf_clearance` para passar a Cloudflare). O servidor devolve o registro real de todo o time e a flag no corpo HTML:

```
CyberZerk{P0int3us3_Qu1_0ubl13_L3s_H3ur3s_Sup}
```

(fr. *"pointeuse qui oublie les heures sup"* — relógio de ponto que esquece as horas extras.)

Request montado em `solve.sh` (o cookie é gerado a partir da variável `manager`); a resposta completa fica em `output.txt`.

## Conclusão

Reto INTRO de **Broken Access Control / IDOR de privilégio**: a aplicação deriva autorização de um dado controlado pelo cliente sem integridade. A correção correta seria manter o papel no lado servidor (sessão assinada/validada) e nunca confiar no cookie. Flag obtida e confirmada (`Correct` na plataforma).

---

## Apêndice — ferramentas

- `solve.sh` — `bash solve.sh`: gera o cookie `profil` forjado (`role=manager`) a partir da variável, dispara o `GET`, salva a resposta em `output.txt` (`tee`) e extrai a flag (`grep -oE`). O `cf_clearance` está anonimizado como `<TOKEN>`; reponha o seu (DevTools → Application → Cookies) antes de rodar.
- `output.txt` — resposta HTML do servidor já com o perfil `manager` (artefato da flag).
