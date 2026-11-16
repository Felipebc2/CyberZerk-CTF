# Regulamento — CTF CyberZerk 2026

Resumo pessoal em PT-BR. O texto oficial (francês) está no site; em caso de dúvida, vale o de lá.

## Resumo rápido

| Item | Valor |
|---|---|
| Organização | Associação CyberZerk (França), gratuito, online |
| Período | **09/11/2026 14h → 22/11/2026 18h (Paris)** = 10h → 14h (Brasília) |
| Formato | Individual: uma conta por pessoa, cada um joga por si |
| Pontuação | Dinâmica: o desafio vale menos quanto mais gente resolve |
| Flag | `CyberZerk{...}` |
| Flag do regulamento | `CyberZerk{J_AI_LU_ET_J_ACCEPTE_LE_REGLEMENT_2026}` (desafio "Signature : règlement", 1 pt) |
| Writeups | Publicação só após o encerramento |
| Contato | `ctf@cyberzerk.fr` ou Discord da associação |

## 01 — Objeto, datas e participação

- Competição de cibersegurança online e gratuita. Ao fim, o placar congela e nenhuma resolução conta mais.
- Inscrição com e-mail válido (confirmar pelo link). Inscrever-se = aceitar o regulamento.
- Aberta a maiores de idade; de 15 anos para cima com autorização do responsável legal.
- Profissionais participam a título pessoal e **só com equipamento próprio**: proibido usar computador, rede ou VPN do empregador.
- Sem prêmios anunciados por enquanto; eventuais prêmios serão divulgados no fim.

## 02 — Equidade, contas e fair-play

Uma conta por pessoa, jogando por si mesma. É proibido:

- criar várias contas ou compartilhar a conta;
- compartilhar flags ou soluções durante a competição, em público (Discord, redes, repositórios de writeup) ou em privado;
- atacar a plataforma, os servidores da organização ou outros participantes. **Escopo = só os subdomínios e IPs explicitamente fornecidos em cada desafio**, e só pelos meios que o desafio prevê. Qualquer scan/intrusão na infra da hospedagem (Hyperion Cloud) ou em sistemas de terceiros é tratado como ataque ilegal;
- perturbar o serviço (DoS, scan massivo);
- tentar contornar as proteções da plataforma;
- assediar, ameaçar, difamar ou se passar por organizador/participante;
- publicar dados pessoais de outros ou acusações falsas.

Falha na própria plataforma: reportar em `ctf@cyberzerk.fr`, **não explorar**. Publicar writeups só depois do encerramento.

## 04 — Detecção, convocação e sanções

- A organização monitora a plataforma e detecta comportamentos anormais (métodos não divulgados). Detecção não é prova: só dispara revisão humana.
- Nenhuma sanção automática. Procedimento:
  1. em caso de dúvida, convocação por e-mail ou Discord para uma conversa de alguns minutos;
  2. o participante explica como chegou na solução (pode ter que refazer uma etapa ou descrever como achou);
  3. pelo menos dois organizadores (ou um + segunda opinião) decidem;
  4. o participante é informado e pode responder em `ctf@cyberzerk.fr`.
- Sanções possíveis: advertência, retirada de pontos de desafios, exclusão do ranking, exclusão da conta. Fraude evidente (resolução claramente automatizada, múltiplas contas) → suspensão imediata e convocação depois. Recusar convocação pode levar à exclusão do ranking.
- **Contestação:** 7 dias após a notificação, por escrito em `ctf@cyberzerk.fr`; revisada por outro membro; depois disso a decisão é definitiva.
- Retaliação contra a organização (assédio, ameaça, difamação, ataque, conta nova para burlar exclusão) = exclusão definitiva.

> Implicação prática: guarde suas anotações e scripts de cada desafio. Se for convocado, você precisa conseguir explicar e refazer a solução.

## 05 — Ranking e desempate

- Ranking pelos pontos dos desafios resolvidos (pontuação dinâmica).
- Empate em geral: quem atingiu a pontuação primeiro fica na frente.
- **Troféus** (pontos bônus, contam no ranking): first blood (primeiro a resolver, exceto desafios de introdução), desafio difícil, desafio extremo, seção completa (todos os desafios de uma categoria). Removidos se o participante for excluído.
- Badge "Donateur" (doação): zero pontos, zero influência.
- **Empate no pódio ou em prêmio:** critério da organização (ver texto oficial); se não der para separar, vale quem chegou à pontuação primeiro.
- Ranking só é definitivo após o encerramento e as verificações (pode levar alguns dias).

## 06 — Dados pessoais (RGPD)

- Coletados: nome de usuário, e-mail, senha (cifrada), IP, histórico de atividade (visualizações, envios, datas/horas).
- Finalidades: operar a competição e o ranking, segurança, verificar o regulamento, estatística agregada para parceiros (nunca dados nominais).
- Retenção: logs com IP 90 dias; contas apagadas/anonimizadas em até 12 meses após o evento.
- Direitos (acesso, retificação, apagamento, oposição, limitação) via `ctf@cyberzerk.fr`; reclamação possível na CNIL.
- Nenhuma sanção é decidida só por tratamento automatizado.

## 07 — Responsabilidades e contato

- Sem garantia de disponibilidade. A organização pode alterar desafio, corrigir pontuação, prorrogar ou suspender a competição (avisa no Discord).
- A associação não se responsabiliza por danos ao seu equipamento causados por arquivos dos desafios (binários, malware, scripts) ou ferramentas de terceiros. **Recomendado usar VM ou container isolado.**
- Regido pela lei francesa; litígios buscam primeiro solução amigável.

## Assinatura

Para confirmar que leu e aceitou o regulamento, envie no desafio **"Signature : règlement"** (categoria Signature, 1 ponto):

```
CyberZerk{J_AI_LU_ET_J_ACCEPTE_LE_REGLEMENT_2026}
```

O envio fica registrado com conta, data, hora e IP, e vale como assinatura.

---

Texto oficial completo (em francês): página "Règlement" em https://ctf.cyberzerk.fr — em caso de dúvida, vale o de lá.
