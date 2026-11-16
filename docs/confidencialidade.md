# Confidencialidade — CTF CyberZerk 2026

Entendimento em PT-BR primeiro; o texto original em francês (fonte de verdade, atualizado em 31/10/2026) está no fim.

## Resumo rápido

| Item | Valor |
|---|---|
| Responsável | Associação CyberZerk |
| Público no placar | Nome de usuário, pontuação e troféus (use pseudônimo se preferir) |
| Logs com IP | 90 dias |
| Conta e atividade | Apagadas/anonimizadas em até 12 meses após o evento |
| Prestadores | Hyperion Cloud (hospedagem), **Cloudflare** (proteção do site), serviço de e-mail, HelloAsso (doações) |
| Cookies | Só sessão e segurança; nada de publicidade/rastreamento |
| Flag de assinatura | `CyberZerk{J_AI_LU_LA_CONFIDENTIALITE_2026}` (desafio "Signature : confidentialité", 1 pt) |

## 01 — Responsável

A associação CyberZerk organiza o CTF e é responsável pelo tratamento dos dados.

## 02 — Dados tratados

- **Conta:** usuário, e-mail, senha (cifrada), país e afiliação se informados.
- **Atividade:** desafios vistos, flags enviadas, datas/horas, pontos, troféus, ranking. Usuário, pontuação e troféus são públicos no placar.
- **Técnicos:** IP, navegador, páginas acessadas (logs do servidor).
- **Doação:** a HelloAsso repassa nome, valor e, se informados, pseudônimos do CTF e do Discord. Gera anúncio no Discord e o badge "Donateur". Nenhum dado bancário chega à associação.
- **E-mails** enviados (confirmação, boas-vindas, encerramento) e contagem de cliques nos links.
- **Assinatura:** o envio nos desafios "Signature" fica registrado com data, hora e IP, como prova de leitura.

## 03 — Finalidades

- Operar a competição: inscrição, validação de flags, ranking.
- Segurança e disponibilidade da plataforma, detecção de abuso e ataque.
- Equidade e cumprimento do regulamento, sempre com revisão humana antes de decidir.
- Estatísticas agregadas para próximas edições e parceiros (nunca dados nominais).

## 04 — Retenção

- Logs com IP: 90 dias.
- Contas e atividade: até 12 meses após o fim do evento.
- Estatísticas agregadas anônimas: mais tempo, para comparar edições.

## 05 — Acesso

Só membros da organização que precisam. Prestadores: Hyperion Cloud, Cloudflare, serviço de e-mail, HelloAsso. Alguns podem tratar dados fora da UE com as garantias legais. Dados não são vendidos nem alugados.

> Implicação prática: o site fica atrás da Cloudflare e hospedado na Hyperion Cloud. Nenhum dos dois está no escopo. Ataque só os alvos indicados em cada desafio.

## 06 — Cookies

Só os necessários (sessão de login) e de segurança.

## 07 — Direitos

Acesso, retificação, apagamento, limitação, oposição via `ctf@cyberzerk.fr`, com resposta em até 1 mês. Reclamação possível na CNIL.

## 08 — Nenhuma decisão automática

Nenhuma sanção ou exclusão é decidida só por tratamento automatizado. Um membro da organização revisa cada caso e o participante pode se explicar.

---

<details>
<summary><b>Texto original (francês)</b></summary>

*Dernière mise à jour : 31 octobre 2026*

### 01 — Qui est responsable

Le CTF CyberZerk est organisé par l'association CyberZerk, responsable du traitement de tes données. Cette page explique ce que nous collectons, pourquoi, combien de temps, et comment exercer tes droits.

### 02 — Les données que nous traitons

- Ton compte : nom d'utilisateur, adresse e-mail, mot de passe (stocké de façon chiffrée), éventuellement pays et affiliation si tu les renseignes.
- Ton activité sur la plateforme : challenges consultés, flags soumis, dates et heures, points, trophées et classement. Ton nom d'utilisateur, ton score et tes trophées sont visibles publiquement dans le classement.
- Des données techniques de connexion : adresse IP, type de navigateur, pages demandées, enregistrées dans les journaux de nos serveurs.
- Si tu fais un don : HelloAsso (qui traite le paiement) nous transmet ton nom, le montant et, si tu les renseignes, ton pseudo CTF et ton pseudo Discord. Nous en tirons une annonce sur le Discord de l'association (prénom et initiale du nom, ou pseudo Discord, et montant) et un badge « Donateur » sur ton profil. Nous ne recevons aucune donnée bancaire.
- Les e-mails que nous t'envoyons (confirmation, bienvenue, message de fin) et le décompte des clics sur les liens qu'ils contiennent.
- Ta signature : si tu valides le règlement et cette page via les challenges « Signature », la soumission est enregistrée avec la date, l'heure et ton adresse IP, comme preuve que tu en as pris connaissance.

### 03 — Pourquoi nous les utilisons

- Faire fonctionner la compétition : inscription, validation des flags, classement (base : l'exécution de ta participation).
- Assurer la sécurité et la disponibilité de la plateforme, et détecter les abus ou attaques (base : notre intérêt légitime).
- Garantir l'équité de la compétition et vérifier le respect du règlement, avec un examen humain avant toute décision (base : notre intérêt légitime).
- Établir des statistiques agrégées (nombre de participants, fréquentation, clics) pour améliorer les prochaines éditions et rendre compte à nos partenaires. Les partenaires ne reçoivent que des chiffres globaux, jamais de données nominatives.

### 04 — Combien de temps

- Journaux techniques contenant des adresses IP : 90 jours, puis supprimés.
- Comptes et activité : supprimés ou anonymisés au plus tard 12 mois après la fin de l'événement.
- Statistiques agrégées sans donnée nominative : conservées plus longtemps pour comparer les éditions.

Le classement public n'affiche que ton nom d'utilisateur et ton score. Choisis un pseudonyme si tu préfères.

### 05 — Qui y a accès

Uniquement les membres de l'organisation qui en ont besoin. Nous nous appuyons sur quelques prestataires techniques : l'hébergeur de nos serveurs (Hyperion Cloud), Cloudflare (protection et accélération du site), notre service d'envoi d'e-mails, et HelloAsso si tu fais un don. Certains peuvent traiter des données hors de l'Union européenne avec les garanties prévues par la réglementation. Nous ne vendons ni ne louons tes données.

### 06 — Cookies

Nous utilisons uniquement les cookies nécessaires au fonctionnement (session de connexion) et à la sécurité du site. Aucun cookie publicitaire ni de suivi.

### 07 — Tes droits

Tu peux demander l'accès à tes données, leur rectification, leur effacement, la limitation ou t'opposer à un traitement, en écrivant à ctf@cyberzerk.fr. Nous répondons dans un délai d'un mois. Si tu estimes que tes droits ne sont pas respectés, tu peux saisir la CNIL.

### 08 — Aucune décision automatique

Aucune sanction ni exclusion n'est décidée par un traitement automatique seul : un membre de l'organisation examine chaque situation, et tu peux t'expliquer (voir le règlement).

### Signature

Pour confirmer que tu as lu et accepté ce document, soumets le code ci-dessous dans le challenge « Signature : confidentialité » (catégorie Signature, 1 point). Ta soumission, enregistrée avec ton compte, la date, l'heure et ton adresse IP, vaut signature.

`CyberZerk{J_AI_LU_LA_CONFIDENTIALITE_2026}`

</details>
