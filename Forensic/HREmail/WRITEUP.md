<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=HR+email" alt="Typing SVG" /></a>

</div>

# HR email — FORENSIC · 🟢 EASY

- **Status:** ✅ RESOLVIDO — e-mail falsificado (spoofing) do "DRH"; flag no anexo MIME em Base64
- **Pontos:** 75
- **Anexo / Alvo:** `note_du_drh.eml` (1,9 KB, SHA256 `5011bc92ef5f3ecdb843eb96bbf2a21ba8215ec3417ab90e2bf62df4e94a324e`)
- **Enunciado:** *"We will send you an internal email from HR, "authentic" according to him. The employees swear they never sent it. Prove where he really comes from and what he's hiding."*
- **Flag:** `CyberZerk{M4il_Sp00f3_P0ur_Surv31ll3r_L3s_Arr3ts}`

---

## TL;DR

1. Um `.eml` é texto puro: cabeçalhos + corpo MIME. Basta abrir num editor.
2. **De onde vem:** `Received`, `Return-Path`, `Reply-To` e `Message-ID` apontam para `mail-cheap-relay.ru` (`45.83.12.207`), e o próprio MX da Tricatel registrou `spf=fail` e `dmarc=fail`. O `From: drh@tricatel-cyber.fr` é forjado.
3. **O que esconde:** o anexo `note_interne_rh.txt` vem em Base64 (`Content-Transfer-Encoding: base64`). Decodificado, traz a "consigne" da Direção e a flag.

## Análise

### 1. Anatomia do `.eml`

Um e-mail tem duas partes separadas por uma linha em branco: os **cabeçalhos** (`Nome: valor`) e o **corpo**. Aqui o corpo é `multipart/mixed`, ou seja, várias partes delimitadas pelo `boundary` `=_cz_boundary_4726`:

| Parte | Content-Type | Encoding | Conteúdo |
|---|---|---|---|
| 1 | `text/plain; charset=UTF-8` | `7bit` (texto legível) | Mensagem curta pedindo para "NÃO divulgar" a nota |
| 2 | `application/octet-stream`, `filename="note_interne_rh.txt"` | `base64` | O anexo, ou seja, o que o e-mail "esconde" |

### 2. Prova da origem real (cabeçalhos)

Os cabeçalhos `Received` são carimbados **por cada servidor que recebe a mensagem**, de baixo para cima. O `From:` é escrito pelo remetente e pode ser qualquer coisa. Por isso a confiança vai para o `Received` adicionado pelo **nosso** MX:

```
Return-Path: <attaquant@mail-cheap-relay.ru>
Received: from vps-unknown.mail-cheap-relay.ru (vps-unknown.mail-cheap-relay.ru [45.83.12.207])
    by mx.tricatel-cyber.fr (Postfix) ...; Fri, 13 Nov 2026 03:14:52 +0100 (CET)
Received-SPF: fail (mx.tricatel-cyber.fr: domain of drh@tricatel-cyber.fr
    does not designate 45.83.12.207 as permitted sender)
Authentication-Results: mx.tricatel-cyber.fr;
    spf=fail smtp.mailfrom=attaquant@mail-cheap-relay.ru;
    dkim=none; dmarc=fail (p=quarantine) header.from=tricatel-cyber.fr
From: "Direction des Ressources Humaines" <drh@tricatel-cyber.fr>
Reply-To: <attaquant@mail-cheap-relay.ru>
Message-ID: <20261113031449.9F2A1@mail-cheap-relay.ru>
```

| Indício | O que prova |
|---|---|
| `Received: from vps-unknown.mail-cheap-relay.ru [45.83.12.207]` | A conexão SMTP veio de um VPS russo, não da infraestrutura da Tricatel |
| `Received-SPF: fail` | O registro SPF de `tricatel-cyber.fr` não autoriza `45.83.12.207` a enviar e-mail pelo domínio |
| `dkim=none` | A mensagem não tem assinatura DKIM, então nada atesta criptograficamente o domínio |
| `dmarc=fail (p=quarantine)` | O `From:` visível (`tricatel-cyber.fr`) não está alinhado com nenhum mecanismo autenticado; a política do domínio manda pôr em quarentena |
| `Return-Path` / `Reply-To` = `attaquant@mail-cheap-relay.ru` | O envelope (`MAIL FROM`) e as respostas vão para o atacante |
| `Message-ID: ...@mail-cheap-relay.ru` | O ID foi gerado pelo servidor do atacante |
| `Date` 03:14 da madrugada | Horário pouco plausível para uma nota interna do RH |

Conclusão: é **e-mail spoofing**. O atacante só preencheu o cabeçalho `From:` com o endereço do DRH; o SMTP não verifica esse campo. Quem verifica é SPF/DKIM/DMARC, e os três falharam.

> Bônus: o `Subject` está em *encoded-word* RFC 2047 (`=?UTF-8?B?...?=`: charset UTF-8, `B` = Base64). Decodificado: `Note interne - “bienveillance”`. É só o título, com aspas tipográficas irônicas.

### 3. O que ele esconde (anexo Base64)

O anexo declarado como `.txt` vem com `Content-Type: application/octet-stream` e Base64. Copiei o bloco entre o cabeçalho da parte 2 e o `--=_cz_boundary_4726--` final e passei pelo **CyberChef → From Base64** (com *Remove non-alphabet chars* marcado, para ignorar as quebras de linha):

```
NOTE INTERNE - CONFIDENTIEL RH
Objet : surveillance des arrets maladie

Consigne de la Direction : contester systematiquement les arrets
de plus de 3 jours et bloquer les acces informatiques du salarie.
Ne pas laisser de trace ecrite cote salarie.

Preuve de l'ordre : CyberZerk{M4il_Sp00f3_P0ur_Surv31ll3r_L3s_Arr3ts}
```

Equivalente na linha de comando: `base64 -d` sobre o bloco extraído, ou `munpack note_du_drh.eml` / `ripmime -i note_du_drh.eml`, que extraem o anexo já decodificado.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Flag no `Subject` codificado (`=?UTF-8?B?...?=`) | ✗ | Decodificado é só `Note interne - “bienveillance”`; o Base64 ali é o encoding normal de cabeçalho com caracteres não-ASCII |
| Flag no corpo `text/plain` | ✗ | Texto em claro (`7bit`) sem flag, só uma piada ("enfin, c'est ce que pretend l'en-tete...") apontando para os cabeçalhos |

## Conclusão

Forense de e-mail introdutória em duas metades, como pede o enunciado. **De onde vem:** os cabeçalhos carimbados pelo MX (`Received`, `Received-SPF`, `Authentication-Results`) desmentem o `From:` e mostram um relay em `45.83.12.207` com SPF e DMARC em falha. **O que esconde:** o anexo MIME em Base64 contém a nota e a flag. Lição: o `From:` é declarativo; a autenticidade de um e-mail se prova pelos cabeçalhos adicionados pelo servidor receptor e por SPF/DKIM/DMARC.

---

## Apêndice — ferramentas

- Editor de texto / `cat note_du_drh.eml`: um `.eml` é texto puro (RFC 5322 + MIME).
- **CyberChef → From Base64** (*Remove non-alphabet chars*): decodifica o `Subject` e o anexo.
- Alternativas CLI: `base64 -d`, `munpack`, `ripmime`. Para cabeçalhos: o "Message Header Analyzer" (Microsoft) ou o `Show original` do Gmail mostram SPF/DKIM/DMARC de forma visual.
