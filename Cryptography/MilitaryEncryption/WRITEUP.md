<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Le+Chiffrement+Militaire" alt="Typing SVG" /></a>

</div>

# Le Chiffrement Militaire (Military Encryption) — CRYPTO · 🟢 EASY

- **Status:** ✅ RESOLVIDO — 3 camadas de Base64, sem chave
- **Pontos:** 100 (Intro, autor Perceval)
- **Anexo / Alvo:** nenhum; o token vem no enunciado
- **Enunciado:** *"Le service IT de Tricatel a réinitialisé vos accès suite à votre arrêt maladie. Ils affirment avoir utilisé un « algorithme de chiffrement militaire à triple couche » pour sécuriser votre mot de passe temporaire. À vue de nez, ça ressemble surtout à un encodage classique répété pour faire illusion... Voici votre token : `VVROc2FWcFlTbUZhV0VweVpUQkpNR042VFRKT1JqbFBUVE5PTUZneFFUQmpNVGxGWkZZNVJHRkVSbTFhYmtsNllsUk9kV1JJTUQwPQ==`"*
- **Flag:** `CyberZerk{B4s364_N3st_P4s_Du_Ch1ffr3m3nt}`

---

## TL;DR

1. "Triple couche" mais "encodage classique répété" significa uma mesma codificação aplicada 3 vezes.
2. O token tem alfabeto `A–Za–z0–9`, termina em `==` e tem 104 caracteres (múltiplo de 4). Isso é **Base64**.
3. No CyberChef, 3× **From Base64** dá a flag. A própria flag resume a lição: "Base64 n'est pas du chiffrement".

## Análise

### 1. Identificar a codificação

| Pista no token | Leitura |
|---|---|
| Só `A–Z`, `a–z`, `0–9` (Base64 também usa `+` e `/`) | alfabeto do **Base64** (64 símbolos) |
| Termina em `==` | **padding** do Base64: completa o último bloco de 4 caracteres |
| 104 caracteres, múltiplo de 4 | o Base64 converte cada 3 bytes em 4 caracteres |
| Começa com `VVRO...` | Base64 de um texto que **já é Base64** costuma gerar prefixos cheios de `V`, `W`, `Z` e `U` maiúsculos |

**Codificação não é criptografia.** O Base64 só muda a representação dos bytes e não tem chave. Qualquer pessoa reverte a operação. Repetir 3 vezes não adiciona segurança nenhuma, só aumenta o tamanho (≈ +33% por camada).

### 2. Descascar as camadas

Cada camada encolhe na proporção 4 → 3 (104 → 76 → 56 → 41):

| Camada | Tamanho | Saída |
|---|---|---|
| 0 (token) | 104 | `VVROc2FWcFlTbUZh...TUQwPQ==` |
| 1 | 76 | `UTNsaVpYSmFaWEpyZTBJMGN6TTJORjlPTTNOMFgxQTBjMTlFZFY5RGFERm1abkl6YlROdWRIMD0=` |
| 2 | 56 | `Q3liZXJaZXJre0I0czM2NF9OM3N0X1A0c19EdV9DaDFmZnIzbTNudH0=` |
| 3 | 41 | `CyberZerk{B4s364_N3st_P4s_Du_Ch1ffr3m3nt}` |

Vale decorar a camada 2: `Q3liZXJaZXJr` é o Base64 de `CyberZerk`. Quando esse prefixo aparece, falta só uma camada.

Receita no CyberChef: `From Base64` → `From Base64` → `From Base64`, com o token **inteiro** no Input.

## O que não funcionou

| Tentativa | Resultado | Por quê |
|---|---|---|
| **From Base85** no CyberChef | ✗ `The all-zero group char cannot appear in the alphabet` | Codificação errada. O token não tem os símbolos do alfabeto Base85 (`!#$%&()*...`) e termina em `=`, que é padding de Base64 |
| Colar só a 2ª linha do token (`GWkZZNVJH...PQ==`, 41 caracteres) | ✗ entrada incompleta | O enunciado quebra o token em duas linhas. É preciso copiar de `VVRO` até `==` (104 caracteres) |

## Conclusão

É um Intro sobre reconhecer codificações. O enunciado já entrega a resposta ("un encodage classique répété pour faire illusion"), e o formato do token confirma: alfabeto, padding `=` e comprimento múltiplo de 4 são a assinatura do Base64. A lição que fica: **codificar não é cifrar**. Sem chave não há segredo, e empilhar camadas só dá a ilusão de segurança.

---

## Apêndice — ferramentas

- CyberChef: 3× "From Base64". Alternativa: a operação "Magic" detecta camadas repetidas automaticamente.
- Equivalente em shell: `echo '<token>' | base64 -d | base64 -d | base64 -d`
