Le portail RH génère chaque jeton de session via getrandbits(32).
tokens.txt : 624 jetons consécutifs interceptés.
secret.bin : la note du DRH, chiffrée par XOR avec les octets des jetons SUIVANTS.
