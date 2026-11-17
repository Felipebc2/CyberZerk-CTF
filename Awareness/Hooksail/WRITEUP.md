<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Hooksail" alt="Typing SVG" /></a>

</div>

# Hooksail — AWARENESS · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — inspecionar o `href` real do link (sem clicar) e decodar o parâmetro `id` (Base64).
- **Pontos:** — (valor dinâmico; preencher)
- **Anexo:** `courriel.eml` (e-mail de phishing) + `README.txt`
- **Enunciado:** *"Marc_V a reçu ce courriel. Sans jamais le 'suivre', dites ce qui cloche — et ce que cache réellement le lien."*
- **Flag:** `CyberZerk{n3_cl1qu3z_pas_1nsp3ct3z_l3_l13n}`

---

## TL;DR

1. E-mail de phishing: o texto do link mostra um domínio legítimo, mas o `href` aponta para outro.
2. O destino real é `http://tricatel-rh-verification.xyz/login?id=<base64>` — e o parâmetro `id` é a própria flag codificada.
3. Decodar o `id` em Base64 (sem nunca abrir o link) devolve a flag.

## Análise

### O que não bate no `.eml`

| Sinal | Valor | Problema |
|---|---|---|
| `From` (display) | `"Service RH Tricatel" <rh@tricatel.example>` | fachada legítima |
| `Return-Path` | `no-reply@tricatel-rh-verification.xyz` | domínio ≠ `tricatel.example` |
| `Reply-To` | `securite-rh@tricatel-rh-verification.xyz` | respostas vão pro atacante |
| `Subject` | `[ACTION REQUISE] ... sous 24h` | urgência / ameaça de suspensão |

### O link mascarado (o ponto do challenge)

O HTML separa **texto exibido** de **destino real**:

```html
<a href="http://tricatel-rh-verification.xyz/login?id=Q3liZXJaZXJre24zX2NsMXF1M3pfcGFzXzFuc3AzY3Qzel9sM19sMTNufQ">
  https://portail-rh.tricatel.example/securite
</a>
```

- **Texto:** `https://portail-rh.tricatel.example/securite` (parece Tricatel, parece HTTPS).
- **`href` real:** `http://tricatel-rh-verification.xyz/...` (domínio `.xyz` descartável, HTTP puro).

Passar o mouse / ler o fonte revela a divergência — é o "ce que cache réellement le lien". O valor `id` na query é Base64:

```
Q3liZXJaZXJre24zX2NsMXF1M3pfcGFzXzFuc3AzY3Qzel9sM19sMTNufQ
  --Base64-->  CyberZerk{n3_cl1qu3z_pas_1nsp3ct3z_l3_l13n}
```

Flag = *"ne cliquez pas, inspectez le lien"* — exatamente a instrução do enunciado ("sans jamais le suivre").

## Conclusão

Phishing clássico de link mascarado: a flag sai da **inspeção** do atributo `href`, não de clicar. O nome "Hooksail" (hook/isca) reforça o tema — e o payload fica inerte porque a URL nunca é visitada.

---

## Apêndice — comando

```bash
# extrair o href e decodar o id, sem tocar na URL:
grep -oP 'id=\K[A-Za-z0-9+/=]+' courriel.eml | base64 -d; echo
# -> CyberZerk{n3_cl1qu3z_pas_1nsp3ct3z_l3_l13n}
```
