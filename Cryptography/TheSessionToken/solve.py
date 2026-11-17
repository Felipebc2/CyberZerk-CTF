#!/usr/bin/env python3
"""The Session Token - MT19937 (getrandbits(32)) state recovery.

624 saidas consecutivas de 32 bits = 1 estado interno completo do Mersenne
Twister. randcrack reconstroi o estado e preve os tokens SEGUINTES. secret.bin
foi XORado com os bytes desses tokens -> prevejo, gero o keystream, XOR, leio.
"""
from pathlib import Path
from randcrack import RandCrack

base = Path(__file__).parent
tokens = [int(x) for x in (base / "tokens.txt").read_text().split()]
secret = (base / "secret.bin").read_bytes()
print(f"[.] {len(tokens)} tokens lidos, secret.bin = {len(secret)} bytes")
assert len(tokens) == 624, "randcrack precisa de exatamente 624 saidas de 32 bits"

# 1) alimenta o estado
rc = RandCrack()
for i, t in enumerate(tokens, 1):
    rc.submit(t)
    if i % 100 == 0:
        print(f"[.] submit {i}/624")
print("[+] estado do MT19937 reconstruido")

# 2) preve os tokens seguintes (4 bytes cada) ate cobrir o secret
n_next = -(-len(secret) // 4)          # ceil(len/4)
nxt = [rc.predict_getrandbits(32) for _ in range(n_next)]
print(f"[+] {n_next} tokens seguintes previstos: {nxt[:3]}...")

# 3) keystream = bytes dos tokens; endianness do portal e' a unica duvida -> testo os 2
for order in ("big", "little"):
    ks = b"".join(t.to_bytes(4, order) for t in nxt)[:len(secret)]
    out = bytes(a ^ b for a, b in zip(secret, ks))
    try:
        txt = out.decode()
        printable = all(32 <= c < 127 or c in (9, 10, 13) for c in out)
    except UnicodeDecodeError:
        txt, printable = repr(out), False
    tag = "<-- LEGIVEL" if printable else ""
    print(f"[{order:>6}] {txt!r} {tag}")
