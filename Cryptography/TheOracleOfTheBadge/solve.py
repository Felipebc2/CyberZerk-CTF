#!/usr/bin/env python3
"""Byte-at-a-time ECB decryption.

Alvo: GET /?data=<hex>  ->  AES-128-ECB( PREFIX(13) || data || SECRET ) em hex.
ECB cifra cada bloco de 16 bytes de forma independente e deterministica, entao
blocos de texto claro iguais viram blocos cifrados iguais. Alinhando o SECRET na
fronteira de um bloco, "adivinhar o segredo" vira "adivinhar 1 byte" (<=256 chutes).

Uso:
  python3 solve.py <BASE_URL> [cf_clearance]   # ex: https://oracle-badge.cyberzerk.fr/
"""
import sys

BLOCK, PREFIX_LEN = 16, 13            # conhecidos do oracle_server.py
FILL = (-PREFIX_LEN) % BLOCK          # 3 bytes de enchimento -> fecha o bloco do prefixo
DROP = PREFIX_LEN + FILL              # ignora 1 bloco inteiro (prefixo) no inicio da cifra

# ordem de chutes: caracteres comuns de flag primeiro, depois o resto do imprimivel, depois o resto
_HOT = (b"abcdefghijklmnopqrstuvwxyz0123456789_"
        b"ABCDEFGHIJKLMNOPQRSTUVWXYZ{}!?.-")
ORDER = bytes(dict.fromkeys(_HOT + bytes(range(32, 127)) + bytes(range(0, 32)) + bytes(range(127, 256))))


def recover(enc, log=True):
    """enc(attacker_bytes) -> cifra crua de AES-ECB(PREFIX || FILL||attacker || SECRET || pad).
    Devolve o SECRET recuperado byte a byte."""
    out = b""
    while True:
        pad = b"A" * (BLOCK - 1 - (len(out) % BLOCK))   # empurra 1 byte desconhecido pro fim do bloco
        blk = (DROP + len(out)) // BLOCK                 # indice do bloco-alvo (ja contando o prefixo)
        target = enc(pad)[blk*BLOCK:(blk+1)*BLOCK]
        hit = next((c for c in ORDER
                    if enc(pad + out + bytes([c]))[blk*BLOCK:(blk+1)*BLOCK] == target), None)
        if hit is None:
            break
        out += bytes([hit])
        if log:
            sys.stdout.write("\r[*] " + out.decode("latin1")); sys.stdout.flush()
        if out.endswith(b"}"):
            break
    if out.endswith(b"\x01"):         # artefato do padding PKCS#7, se nao parou no '}'
        out = out[:-1]
    return out


def http_oracle(base, cookie=None):
    import requests
    ua = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
          "(KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36")
    s = requests.Session()
    if cookie:
        s.cookies.set("cf_clearance", cookie); s.headers["User-Agent"] = ua
    st = {"n": 0}
    def enc(attacker):
        st["n"] += 1
        data = (b"A" * FILL + attacker).hex()
        r = s.get(base, params={"data": data}, timeout=30)
        txt = r.text.strip()
        try:
            return bytes.fromhex(txt)
        except ValueError:
            raise SystemExit("\n[!] resposta nao-hex (HTTP %d) apos %d req. "
                             "Provavel bloqueio Cloudflare -> pegue um cf_clearance fresco.\n"
                             "    inicio da resposta: %r" % (r.status_code, st["n"], txt[:160]))
    return enc, st


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("uso: python3 solve.py <BASE_URL> [cf_clearance]")
    enc, st = http_oracle(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    secret = recover(enc)
    print("\n[+] SECRET = " + secret.decode("latin1"))
    print("[+] requisicoes ao oraculo: %d" % st["n"])
