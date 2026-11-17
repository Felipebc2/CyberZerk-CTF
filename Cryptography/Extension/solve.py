#!/usr/bin/env python3
"""Extension - Hash Length Extension + AES-256-ECB.

tag = SHA256(secret || message), secret de 16 bytes. O digest E' o estado interno
final do Merkle-Damgard: quem tem o digest + o comprimento absorvido pode fingir que
o SHA256 "continuou" e anexar bytes, sem conhecer o secret. sha256ext.extend() faz
exatamente isso. O tag forjado vira a chave AES-256-ECB que decifra cipher.bin.
"""
from pathlib import Path
from sha256ext import extend, glue
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

base = Path(__file__).parent
message = b"user=marc_v&role=stagiaire"
tag = bytes.fromhex("f81761886a0a96024db3864147e1650b7afe8e196eef08ec34182109d5f25670")
secret_len = 16
append = b"&role=admin"
cipher = (base / "cipher.bin").read_bytes()

orig_len = secret_len + len(message)   # 16 + 26 = 42 = tamanho de (secret||message)
print(f"[.] orig_len = {secret_len} (secret) + {len(message)} (message) = {orig_len}")
print(f"[.] glue (padding de cola) = {glue(orig_len)!r}")

forged = extend(tag, orig_len, append)
print(f"[+] tag forjado = {forged.hex()}")
print(f"[.] mensagem que o servidor validaria = message || glue || {append!r}")

print(f"[.] cipher.bin = {len(cipher)} bytes, decifrando AES-256-ECB com o tag forjado...")
pt = AES.new(forged, AES.MODE_ECB).decrypt(cipher)
try:
    flag = unpad(pt, 16)
except ValueError:
    flag = pt  # sem PKCS7 valido -> mostra cru
print(f"[+] {flag!r}")
