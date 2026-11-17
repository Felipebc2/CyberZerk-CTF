<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Crisis+Dump" alt="Typing SVG" /></a>

</div>

# Crisis Dump — FORENSIC · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — chave de API removida do `deploy.sh` com um novo commit, recuperada do commit anterior pelo histórico do Git
- **Pontos:** 150
- **Anexo / Alvo:** `depot_intranet.tgz` (tar + gzip, 13,8 KB comprimido / 80 KB descomprimido, SHA256 `daff512f6e9fe48e7935b141dee704ffc0b4d4c601dca615e0662cd9f00ae455`) com o repositório Git `depot/`
- **Enunciado:** *"Here is a copy of the Git repository of the Tricatel intranet, retrieved before the departure of a dev. He swears he 'removed the secret from the code'. A secret removed from the code did not necessarily leave history."*
- **Flag:** `CyberZerk{G1t_N0ubl13_J4m41s_R13n_Du_P4ss3}`

---

## TL;DR

1. O `.tgz` traz um repositório Git completo: a árvore de trabalho atual (`config.py`, `deploy.sh`) e a pasta `.git/` com todo o histórico.
2. O reflog (`.git/logs/HEAD`) lista 4 commits, um deles *"Securisation: cle sortie du code (lue depuis env)"*.
3. Esse commit só substituiu a chave por `$DEPLOY_API_KEY`. O `git show` dele mostra a linha apagada, e a linha apagada é a flag.

## Análise

### 1. Identificar o anexo

```bash
file depot_intranet.tgz        # gzip compressed data, original size ... 81920
tar -tzvf depot_intranet.tgz   # lista sem extrair
```

`.tgz` é um `tar` comprimido com `gzip`. A listagem mostrou `depot/config.py` e `depot/.git/`, com `objects/`, `logs/`, `refs/` e hooks. A presença do `.git/` muda tudo: ele guarda **todos** os commits, não só o estado atual dos arquivos.

### 2. Extrair com cuidado

```bash
tar -xzf depot_intranet.tgz
cat depot/.git/config
```

Um repositório de terceiros pode ter um `.git/config` malicioso. Opções como `core.fsmonitor`, `core.pager` ou `core.sshCommand` executam comandos assim que você roda `git status` ou `git log`, e um prompt de shell que mostra a branch (`depot master`) já roda `git` sozinho ao entrar na pasta. Aqui o `config` só tinha `[core]` padrão e `[user]` (`IT Tricatel <it@tricatel.local>`), e os hooks eram todos `.sample`, que não rodam.

### 3. Ler o histórico pelo reflog

O reflog registra cada movimento do `HEAD`, e está em texto puro:

```bash
cat depot/.git/logs/HEAD
```

| Commit | Mensagem | O que mudou |
|---|---|---|
| `e04f057` | Init config intranet | cria `config.py` (`DEBUG`, `DB_HOST = "10.0.0.5"`) |
| `36e1d6e` | Ajout script de deploiement | cria `deploy.sh` **com a chave em claro** |
| `b3fc794` | Securisation: cle sortie du code (lue depuis env) | troca a chave por `$DEPLOY_API_KEY` |
| `db83693` | MAJ config | acrescenta `fin config` ao `config.py` (ruído) |

A mensagem de `b3fc794` entrega o caso: a chave "saiu do código" e passou a ser lida de uma **variável de ambiente**. Ou seja, ela estava no código no commit anterior.

### 4. Ler um commit antigo sem "voltar" o repositório

Um commit é um **snapshot** imutável. Para lê-lo não é preciso `git checkout`, que reescreveria a árvore de trabalho e, em forense, alteraria a evidência. O `git show` lê direto dos objetos:

```bash
git show 36e1d6e           # o commit e o diff contra o pai
git show b3fc794           # o commit da "limpeza": as linhas "-" são o que foi apagado
git show 36e1d6e:deploy.sh # o arquivo inteiro como estava naquele commit
```

```diff
diff --git a/deploy.sh b/deploy.sh
@@ -1,4 +1,4 @@
 #!/bin/sh
-# Script de déploiement - NE PAS COMMITER LES SECRETS
-API_KEY="CyberZerk{G1t_N0ubl13_J4m41s_R13n_Du_P4ss3}"
-echo "Déploiement avec $API_KEY"
+# Script de déploiement
+API_KEY="$DEPLOY_API_KEY"   # lu depuis l'environnement maintenant
+echo "Déploiement"
```

O comentário *"NE PAS COMMITER LES SECRETS"* estava logo acima da chave commitada.

### 5. Confirmar que não há mais nada

```bash
git log --all -S 'CyberZerk' --format='%h %s'   # 36e1d6e (adiciona) e b3fc794 (remove)
git fsck --lost-found                           # nenhum objeto órfão
```

O `-S` (*pickaxe*) lista os commits que mudam o número de ocorrências de uma string: um adicionou a flag e o outro a removeu. Os 12 objetos soltos em `.git/objects` são exatamente os 12 alcançáveis pelos commits (4 commits, 4 trees, 4 blobs), então não há commit apagado nem stash escondido.

A flag descreve a lição: *"Git n'oublie jamais rien du passé"*, o Git não esquece nada do passado.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| O segredo estava no `config.py` | ✗ (falsificada) | Na triagem só o `config.py` aparecia na listagem do tar, mas o `git show b3fc794` mostrou que a chave estava no `deploy.sh` |
| "Commit do `.env`" | ✗ (leitura errada) | A mensagem *"lue depuis env"* fala de variável de ambiente (`$DEPLOY_API_KEY`), não de um arquivo `.env` |
| Último commit `MAJ config` | ✗ (ruído) | Só acrescenta `fin config` ao `config.py` |

## Conclusão

Forense de repositório Git: o estado atual dos arquivos é só a ponta do histórico. Um commit que "remove" um segredo apenas cria um snapshot novo sem ele, e todos os anteriores continuam em `.git/objects`. Para achar o segredo, basta ler o reflog ou o `git log`, olhar o diff do commit de "limpeza" e, para varrer tudo, usar `git log -p --all -S '<string>'`.

Lição defensiva: um segredo commitado está **vazado**, e a única correção real é **revogar e rotacionar** a chave. Reescrever o histórico (`git filter-repo`, BFG) ajuda, mas não alcança clones e cópias já feitos, como este dump feito antes da saída do dev. Para prevenir, use um scanner de segredos no pre-commit (gitleaks, trufflehog) e mantenha segredos fora do repositório desde o primeiro commit.

---

## Apêndice — ferramentas

- `tar -tzvf X.tgz` para listar e `tar -xzf X.tgz` para extrair.
- `cat .git/logs/HEAD`: reflog em texto puro, com todos os movimentos do `HEAD`.
- `git log --all --stat` / `git log -p --all`: histórico com arquivos alterados ou diffs completos.
- `git show <commit>` e `git show <commit>:<arquivo>`: leem um snapshot antigo sem tocar na árvore de trabalho.
- `git log --all -S '<string>'` e `git rev-list --all | xargs git grep '<string>'`: procuram uma string em todo o histórico.
- `git fsck --lost-found`: objetos órfãos (commits apagados, stashes, `reset --hard`).
- Scanners automáticos: `gitleaks detect`, `trufflehog git file://.`.
