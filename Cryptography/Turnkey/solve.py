#!/usr/bin/env python3
"""Turnkey - RSA com primos proximos (gerador 'caseiro' feito as pressas).

Ataque: fatoracao de Fermat. Se p e q estao perto, n = a^2 - b^2 com 'a' logo
acima de sqrt(n), entao achamos p,q em poucos passos. So biblioteca padrao
(math.isqrt aguenta inteiros gigantes; pow(e,-1,phi) faz o inverso modular).
"""
from math import isqrt

n = 80212772058200318331300079496309046404407863541893990823458017701424496169728020886315708954946247456549467636228289508051504043657362562710963459898059618322307640646997491893098662379623269687517308992271177299514157669726203684540391560112332919658354699766234227531947934780484232345671991558901521674857
e = 65537
c = 37349549515090945417450122795335580990902750723340185050711772061916623126113099880177602219381069951334085720404628406456724149937589057117852268813232105608362675774617868234377809159128266125490782550531069542420297187328167250214392422812890728320489416372899423467921565710232771608025776495955836994422

# Fermat: sobe 'a' a partir de ceil(sqrt(n)) ate a^2 - n virar quadrado perfeito
a = isqrt(n) + 1
steps = 0
while True:
    b2 = a * a - n
    b = isqrt(b2)
    if b * b == b2:            # achou: b2 e quadrado perfeito
        break
    a += 1
    steps += 1
    if steps % 100000 == 0:
        print(f"[.] {steps} passos... (se passar de milhoes, NAO e Fermat)")

p, q = a + b, a - b
assert p * q == n, "p*q != n"
print(f"[+] fatorado em {steps} passos")
print(f"[+] p = {p}")
print(f"[+] q = {q}")

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)           # inverso modular de e mod phi (Python 3.8+)
m = pow(c, d, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(f"[+] flag: {flag.decode(errors='replace')}")
