#!/usr/bin/env python3
"""Signature Unique - ECDSA nonce reuse (secp256k1).

Dois ECDSA assinados com o MESMO nonce k (r1 == r2 denuncia isso). Como
  s = k^-1 * (z + r*d) mod n,
dois s com o mesmo k e r se subtraem e matam o d:
  s1 - s2 = k^-1 * (z1 - z2)  ->  k = (z1 - z2) / (s1 - s2) mod n
e com k de volta:
  d = (s1*k - z1) / r mod n
Com a chave privada d, a flag abre: AES-256-ECB, chave = SHA256(str(d)).
"""
import hashlib, json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

# ordem do grupo secp256k1 (constante publica da curva)
n = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

base = Path(__file__).parent
sig = json.loads((base / "signatures.json").read_text())

def z(msg):
    # ECDSA usa o hash da mensagem como inteiro (n tem 256 bits = SHA256, sem truncar)
    return int.from_bytes(hashlib.sha256(msg.encode()).digest(), "big")

r1, s1, z1 = sig["r1"], sig["s1"], z(sig["msg1"])
r2, s2, z2 = sig["r2"], sig["s2"], z(sig["msg2"])

print(f"[.] r1 == r2 ? {r1 == r2}  -> nonce k reusado" if r1 == r2 else "[!] r1 != r2, ataque nao se aplica")

k = (z1 - z2) * pow(s1 - s2, -1, n) % n
print(f"[+] nonce k  = {k}")

d = (s1 * k - z1) * pow(r1, -1, n) % n
print(f"[+] chave privada d = {d}")

key = hashlib.sha256(str(d).encode()).digest()
print(f"[.] chave AES = SHA256(str(d)) = {key.hex()}")

ct = (base / "vault.bin").read_bytes()
pt = AES.new(key, AES.MODE_ECB).decrypt(ct)
try:
    flag = unpad(pt, 16)
except ValueError:
    flag = pt
print(f"[+] {flag!r}")
