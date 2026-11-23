#!/usr/bin/env bash
# Avisa quando aparecem challenges novos no CTF CyberZerk.
# VOCÊ roda; eu nunca disparo contra a plataforma (regra nº1).
# Requer: curl, jq, (opcional) notify-send.
set -euo pipefail

BASE="${CYBERZERK_URL:-https://ctf.cyberzerk.fr}"
TOKEN_FILE="${CYBERZERK_TOKEN_FILE:-$HOME/.config/cyberzerk/token}"
STATE="${CYBERZERK_STATE:-$HOME/.cache/cyberzerk-challenges.txt}"
INTERVAL="${CYBERZERK_INTERVAL:-300}"   # segundos entre checagens

# E-mail via SMTP (Gmail). SMTP_PASS_FILE = app password de 16 chars (exige 2FA).
EMAIL_TO="${CYBERZERK_EMAIL_TO:-}"
SMTP_HOST="${CYBERZERK_SMTP_HOST:-smtp.gmail.com}"
SMTP_PORT="${CYBERZERK_SMTP_PORT:-465}"
SMTP_USER="${CYBERZERK_SMTP_USER:-$EMAIL_TO}"
SMTP_PASS_FILE="${CYBERZERK_SMTP_PASS_FILE:-$HOME/.config/cyberzerk/smtp-pass}"

# --- self-test offline (não toca na rede): ./watch-challenges.sh --test ---
if [[ "${1:-}" == --test ]]; then
  antes=$(printf '%s\n' 'web | A' 'web | B' | sort)
  depois=$(printf '%s\n' 'web | A' 'web | B' 'crypto | C' | sort)
  got=$(comm -13 <(echo "$antes") <(echo "$depois"))
  [[ "$got" == "crypto | C" ]] && { echo "self-test OK"; exit 0; } || { echo "self-test FAIL: '$got'"; exit 1; }
fi

fetch() {  # imprime "categoria | nome" por linha, ordenado
  curl -fsS "$BASE/api/v1/challenges" \
    -H "Authorization: Token $(cat "$TOKEN_FILE")" \
    -H 'Content-Type: application/json' \
  | jq -r '.data[] | "\(.category) | \(.name)"' | sort
}

notify() {
  echo "  [NOVO] $1"
  command -v notify-send >/dev/null && notify-send -u critical "CTF: challenge novo" "$1" || true
}

mkdir -p "$(dirname "$STATE")"
echo "Observando $BASE a cada ${INTERVAL}s. Ctrl-C para parar."

while true; do
  if now=$(fetch); then
    if [[ -f "$STATE" ]]; then
      novos=$(comm -13 "$STATE" <(echo "$now") || true)
      if [[ -n "$novos" ]]; then
        while IFS= read -r l; do [[ -n "$l" ]] && notify "$l"; done <<<"$novos"
      else
        echo "$(date +%H:%M) sem novidades ($(grep -c . <<<"$now") challenges)"
      fi
    else
      echo "$(date +%H:%M) baseline: $(grep -c . <<<"$now") challenges salvos"
    fi
    echo "$now" > "$STATE"
  else
    echo "$(date +%H:%M) falha ao buscar (token expirado? offline? endpoint diferente?)"
  fi
  sleep "$INTERVAL"
done
