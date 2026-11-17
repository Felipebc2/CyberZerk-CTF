<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Sick+leave" alt="Typing SVG" /></a>

</div>

# Sick leave — WEB (INTRO) · 🟢 FÁCIL

- **Status:** ✅ RESOLVIDO — IDOR: troca do `dossier_id` na URL dá acesso ao dossiê de outro funcionário
- **Pontos:** 100
- **Anexo / Alvo:** `https://absences.cyberzerk.fr/` (portal de ausências RH)
- **Enunciado:** *"The absence portal is online. You have access to your own leave request file. A colleague took sick leave yesterday following unbearable pressure from management, his file must be just before yours. Find a way to read his absence report."*
- **Flag:** `CyberZerk{ID0R_M4n4g3m3nt_T0x1qu3}`

---

## TL;DR

1. O portal mostra o seu dossiê via `?dossier_id=1042`, escolhido por um **ID sequencial na URL**.
2. O servidor **não verifica se o dossiê pertence a você** — é um **IDOR** (Insecure Direct Object Reference / Broken Access Control).
3. O enunciado diz que o arquivo do colega está "logo antes do seu" → trocar para `?dossier_id=1041` entrega o dossiê dele com a flag.

## Análise

### Recon

Autenticado como **Employé #8472 (Droits standards)**, a própria URL controla qual dossiê é exibido:

```
https://absences.cyberzerk.fr/?dossier_id=1042
```

→ `Dossier #1042 - Demande de Congés` (o seu). O recurso é referenciado diretamente por um identificador previsível e **sequencial**.

### Confirmação — não há checagem de acesso

Trocando para `?dossier_id=0`, o app responde:

```
File #0
Folder not found or you don't have read rights
(lol, as if we were really checking the rights).
```

A mensagem confessa explicitamente que **a permissão não é validada** — qualquer ID existente é servido a qualquer usuário autenticado. É a definição de IDOR.

### Exploração

O enunciado aponta o alvo: o colega tirou atestado "ontem" e o arquivo dele está **imediatamente antes** do seu (`1042`). Basta decrementar:

```
https://absences.cyberzerk.fr/?dossier_id=1041
```

→ `Dossier #1041 - Arrêt Maladie Prolongé`, de **Marc V. (Développeur Senior)**, com o relatório médico (burn-out) e, ao final, a flag:

```
CyberZerk{ID0R_M4n4g3m3nt_T0x1qu3}
```

(IDOR + "management toxique" — o tema do reto.)

> Se `1041` não fosse o alvo, bastaria varrer os IDs vizinhos (`1040`, `1043`, …), já que são sequenciais e sem controle de acesso.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| `?dossier_id=0` | ✗ | ID inexistente; serviu só pra confirmar a ausência de checagem de permissão |

## Conclusão

Reto INTRO de **IDOR / Broken Access Control**: o servidor expõe objetos por um identificador direto e previsível sem verificar se o usuário tem direito àquele recurso. A correção é **autorização por objeto** no servidor (checar que o `dossier_id` pertence ao usuário da sessão, ou usar identificadores não adivinháveis + ACL). Flag obtida e confirmada na plataforma.

---

## Apêndice — ferramentas

- Nenhuma. A exploração foi manual: editar o parâmetro `dossier_id` na barra de endereço do navegador (`1042` → `1041`). Opcionalmente, o mesmo request via `curl --url 'https://absences.cyberzerk.fr/?dossier_id=1041'` com o cookie de sessão.
