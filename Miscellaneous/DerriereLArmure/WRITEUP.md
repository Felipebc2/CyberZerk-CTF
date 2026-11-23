<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Derriere+l'Armure" alt="Typing SVG" /></a>

</div>

# Derrière l'Armure — SECRET · 🟣 EXTREMO

- **Status:** ✅ RESOLVIDO — desafio oculto encontrado pela página de *lore* `/prologue`
- **Pontos:** 500 (+ troféu *Section complète : Secret* 30)
- **Autor:** Perceval
- **Alvo:** `https://ctf.cyberzerk.fr/prologue` → endpoint `POST /api/v1/challenges/secret/armure`
- **Enunciado:** *"Tu as pris le temps de regarder derrière l'armure. Beaucoup ne le font jamais. (...) Ce challenge ne cache aucune faille à exploiter. Il est là pour te rappeler qu'un homme qui parle de ce qu'il traverse n'est pas moins fort : il est plus solide. (...) « Et moi, comment je vais, vraiment ? » (...) le 3114 répond gratuitement, 24 h sur 24. Valide la clé que tu as trouvée : ces 500 points sont pour toi, pour avoir osé regarder derrière l'armure."*
- **Flag:** `CyberZerk{le_masque_tombe_et_les_cheaters_tombent_aussi}`

---

## TL;DR

1. Challenge **oculto** (categoria *Secret*, não aparece em `/challenges`). O enigma é **onde** ele está — não há vuln a explorar (Movember: metáfora da armadura / saúde emocional masculina).
2. O caminho é a página de *lore* **`/prologue`** ("Opération CyberZerk : Derrière l'Écran"). No texto, a palavra **`armure`** é um `<span id="armure">` clicável.
3. **Clicar na palavra 3×** (estando logado) dispara `POST /api/v1/challenges/secret/armure`; o servidor devolve a flag ("Fissure Système Détectée"). Copia → valida no challenge *Derrière l'Armure*.

## Análise

### Descoberta — onde fica o desafio

O challenge não lista em `/challenges`. As pistas públicas convergiam para o tema "armadura" (nome *Derrière l'Armure*, Movember, mascote berserker), mas o **local** só apareceu lendo o **fonte público** de `/prologue` (GET read-only, sem autenticar):

- Endpoint custom no HTML: `POST /api/v1/challenges/secret/armure`.
- Na narrativa, `...regarder ce qui se passe derrière l'<span id="armure">armure</span>`.

### A mecânica — JS embutido em `/prologue`

O `<script>` da página entrega tudo em claro:

```js
var mot = document.getElementById('armure');
var clics = 0, ouvert = false;

function demander() {
  if (!(window.init||{}).userId) return Promise.resolve({statut:401});
  return fetch('/api/v1/challenges/secret/armure', {
    method:'POST', credentials:'same-origin',
    headers:{'Content-Type':'application/json','CSRF-Token':window.init.csrfNonce},
    body:'{}'
  }).then(r => r.json().then(j => ({statut:r.status, json:j})));
}

mot.addEventListener('click', function () {
  if (ouvert) return;
  clics++;
  if (clics < 3) return;          // precisa de 3 cliques
  ouvert = true;
  var reponse = demander();
  document.body.style.filter = 'invert(1) hue-rotate(180deg)';  // tela inverte ~1s
  setTimeout(() => { document.body.style.filter='none'; reponse.then(afficher); }, 1000);
});
```

Respostas do servidor (decididas server-side):

| Status | Significado |
|---|---|
| `200 success` | devolve `{flag, name, challenge_id}` → mostra a clé dourada + "Ouvrir la porte" |
| `401 / 302` | não logado → "connecte-toi, puis reviens ici" |
| `403` | antes do lançamento → "Reviens quand l'opération sera lancée" |

### Execução

Logado em `ctf.cyberzerk.fr`, abrir `/prologue`, rolar até *"...derrière l'armure"* e clicar em **`armure` 3×**. A tela inverte ~1s e aparece **"Fissure Système Détectée"** com a flag. Validada no challenge → ✅ *Correct* (50 solves no momento).

## O que não funcionou

A maior parte do tempo foi gasto numa rota paralela (imagem/stego) sugerida por uma dica de Discord e pelo post de LinkedIn. Não era o caminho.

| Hipótese | Resultado | Por quê |
|---|---|---|
| LSB / bit-plane visual no mascote | ✗ | planos só reexpõem a arte binária do capacete, sem camada escondida |
| Metadata/append no ícone do LinkedIn | ✗ | JPEG 200×200 13 kB limpo; LinkedIn re-encoda e remove EXIF |
| Blobs hex do `/prologue` | ✗ | não decodaram em texto (XOR A0/AA/20/FF/80) — ruído/integridade |
| Perfil "Vincent Julien M." (tag da CyberZerk) | ✗ | nada relevante |

**Rota paralela útil só como fingerprint** — a cifra que a org usa (`From Hex → Vigenère`):

- Legenda do post oficial, chave **CYBERZERK** → *"Rendez-vous le 9 Novembre"*.
- Comentário (bloco 🔑 = pergunta do *Guia do Mochileiro* → **42**), chave **42** → *"il se passe quelque chose de sympa le 9 novembre"*.

Ambos eram **teasers de lançamento**, não a flag.

## Conclusão

A "dificuldade extrema" era puramente de **descoberta**: perceber que a página de narrativa tinha uma palavra clicável que, após 3 cliques, pedia a flag ao servidor pela porta oficial `/api/v1/challenges/secret/armure`. Nenhuma exploração — o próprio enunciado confirma *"ne cache aucune faille à exploiter"*. Ler o fonte público do `/prologue` transformou o enigma em receita. A ironia fica na flag: `le_masque_tombe_et_les_cheaters_tombent_aussi`.
