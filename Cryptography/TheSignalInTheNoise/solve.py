"""The Signal in the Noise: LWE (n=40, m=80, q=3329) via Kannan embedding + LLL/BKZ progressivo.

Uso:  .venv/bin/python -I solve.py [--bg] [signal.json]
      .venv/bin/python -I solve.py --selftest [eta_e] [eta_s] [--bg]
        eta_e = amplitude do erro sintético; eta_s = amplitude de s (0 = uniforme mod q)
        --bg  = embedding Bai-Galbraith (vetor curto (e, s, 1)), para segredo pequeno
"""
import hashlib
import json
import math
import random
import sys
import time

from Crypto.Cipher import AES
from fpylll import BKZ, LLL, IntegerMatrix

STAGES = [("LLL", None)] + [("BKZ", bs) for bs in (10, 20, 30, 40, 50)]


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def build_basis(A, b, q, M=1):
    # Linhas geradoras: colunas de A (combinações A·s), q·eᵢ (o "mod q") e (b, M).
    # O vetor curto esperado é (b − A·s mod q, M) = (e, M).
    m, n = len(A), len(A[0])
    rows = [[A[i][j] for i in range(m)] + [0] for j in range(n)]
    rows += [[q if k == i else 0 for k in range(m)] + [0] for i in range(m)]
    rows.append(list(b) + [M])
    return rows


def rows_of(B):
    return [[B[i, j] for j in range(B.ncols)] for i in range(B.nrows)]


def build_bg(A, b, q, M=1):
    # Bai-Galbraith: o vetor curto é (e, s, M), útil quando s também é pequeno.
    # Linhas: (−coluna_j de A, unitário_j, 0), (q·eᵢ, 0, 0) e (b, 0, M). Base quadrada, posto cheio.
    m, n = len(A), len(A[0])
    rows = [[-A[i][j] for i in range(m)] + [1 if k == j else 0 for k in range(n)] + [0] for j in range(n)]
    rows += [[q if k == i else 0 for k in range(m)] + [0] * n + [0] for i in range(m)]
    rows.append(list(b) + [0] * n + [M])
    return rows


def candidates(B, M):
    """Vetores com última coordenada ±M, normalizados para +M, do mais curto ao mais longo."""
    out = []
    for row in rows_of(B):
        if abs(row[-1]) == M and any(row[:-1]):
            sign = 1 if row[-1] == M else -1
            out.append([sign * x for x in row[:-1]])
    return sorted(out, key=lambda v: sum(x * x for x in v))


def solve_mod(A, y, q):
    """Gauss mod q (q primo) em A·s = y, com m ≥ n equações."""
    m, n = len(A), len(A[0])
    T = [row[:] + [yi % q] for row, yi in zip(A, y)]
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if T[i][c] % q), None)
        if p is None:
            raise ValueError(f"coluna {c} sem pivô: sistema subdeterminado")
        T[r], T[p] = T[p], T[r]
        inv = pow(T[r][c], -1, q)
        T[r] = [x * inv % q for x in T[r]]
        for i in range(m):
            if i != r and T[i][c] % q:
                f = T[i][c]
                T[i] = [(x - f * z) % q for x, z in zip(T[i], T[r])]
        r += 1
    return [T[i][n] for i in range(n)]


def recover(A, b, q, accept, bg=False, M=1):
    """Reduz a base em estágios crescentes; para quando `accept(s)` confirmar (tag GCM ou s conhecido).

    Atenção: b == A·s + e (mod q) vale para QUALQUER candidato do reticulado, então não serve de prova.
    """
    m, n = len(A), len(A[0])
    dim, logdet = (m + n + 1, m) if bg else (m + 1, m - n)
    gh = math.sqrt(dim / (2 * math.pi * math.e)) * q ** (logdet / dim)
    log(f"modo {'Bai-Galbraith (e, s, 1)' if bg else 'primal (e, 1)'}: heurística gaussiana ≈ {gh:.0f}, "
        f"o vetor alvo precisa ser bem menor que isso")
    B = IntegerMatrix.from_matrix(build_bg(A, b, q, M) if bg else build_basis(A, b, q, M))
    log(f"base {B.nrows}x{B.ncols}")
    tested = set()
    for kind, bs in STAGES:
        t = time.time()
        if kind == "LLL":
            LLL.reduction(B)  # geradores dependentes viram linhas nulas no topo
            B = IntegerMatrix.from_matrix([r for r in rows_of(B) if any(r)])
        else:
            # sem arquivo de estratégias no wheel do pip: BKZ nativo sem poda, com auto-abort
            BKZ.reduction(B, BKZ.Param(block_size=bs, max_loops=8, flags=BKZ.AUTO_ABORT | BKZ.MAX_LOOPS))
        norms = sorted(math.isqrt(sum(x * x for x in r)) for r in rows_of(B))[:3]
        cands = candidates(B, M)
        best = math.isqrt(sum(x * x for x in cands[0])) if cands else None
        log(f"{kind}{'' if bs is None else f'-{bs}'} em {time.time() - t:.1f}s | "
            f"3 menores normas {norms} | melhor alvo: {best} ({len(cands)} candidatos)")
        for v in cands:
            key = tuple(v)
            if key in tested:
                continue
            tested.add(key)
            e = v[:m]
            s = [x % q for x in v[m:m + n]] if bg else solve_mod(A, [bi - ei for bi, ei in zip(b, e)], q)
            if accept(s):
                log(f"ACEITO: ‖e‖ ≈ {math.isqrt(sum(x * x for x in e))}, e em [{min(e)}, {max(e)}]")
                return s, e
        log("  nenhum candidato confirmado, aumentando o bloco")
    raise SystemExit("FALHOU até BKZ-50: o vetor alvo não é curto o bastante (hipótese falsificada)")


def gcm_oracle(q, data):
    nonce, ct, tag = (bytes.fromhex(data[k]) for k in ("nonce", "ct", "tag"))
    found = {}

    def accept(s):
        centered = [x - q if x > q // 2 else x for x in s]
        for label, coeffs in (("s em [0, q)", s), ("s centrado", centered)):
            key = hashlib.sha256(",".join(map(str, coeffs)).encode()).digest()
            try:
                found["pt"] = AES.new(key, AES.MODE_GCM, nonce=nonce).decrypt_and_verify(ct, tag)
            except ValueError:
                continue
            found["label"] = label
            return True
        return False

    return accept, found


def selftest(eta_e, eta_s, bg):
    q, n, m = 3329, 40, 80
    rnd = random.Random(1234)
    s = [rnd.randint(-eta_s, eta_s) % q if eta_s else rnd.randrange(q) for _ in range(n)]
    A = [[rnd.randrange(q) for _ in range(n)] for _ in range(m)]
    e = [rnd.randint(-eta_e, eta_e) for _ in range(m)]
    b = [(sum(a * x for a, x in zip(A[i], s)) + e[i]) % q for i in range(m)]
    log(f"selftest: n=40 m=80 q=3329, e em [-{eta_e}, {eta_e}], "
        f"s {'em [-%d, %d]' % (eta_s, eta_s) if eta_s else 'uniforme mod q'}")
    s2, e2 = recover(A, b, q, accept=lambda cand: cand == s, bg=bg)
    assert s2 == s and e2 == e, "selftest falhou"
    log("selftest OK: s e e recuperados exatamente")


def main():
    bg = "--bg" in sys.argv
    args = [a for a in sys.argv[1:] if a not in ("--bg", "--selftest")]
    if "--selftest" in sys.argv:
        nums = [int(a) for a in args] + [2, 0][len(args):]
        return selftest(nums[0], nums[1], bg)
    path = args[0] if args else "signal.json"
    data = json.load(open(path))
    q, A, b = data["q"], data["A"], data["b"]
    log(f"carregado {path}: q={q}, A {len(A)}x{len(A[0])}, b {len(b)}")
    accept, found = gcm_oracle(q, data)
    s, _ = recover(A, b, q, accept, bg=bg)
    log(f"tag GCM VALIDOU com {found['label']}")
    log(f"s = {s}")
    print("\nPLAINTEXT:\n" + found["pt"].decode(errors="replace"), flush=True)


if __name__ == "__main__":
    main()
