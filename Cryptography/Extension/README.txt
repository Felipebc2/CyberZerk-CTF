Le cookie RH = message + tag, ou tag = SHA256(secret || message), secret de 16 octets.
Le coffre s'ouvre si vous presentez un tag valide pour message||...||'&role=admin'.
cipher.bin est chiffre en AES-256-ECB, cle = ce tag forge (32 octets bruts du digest).
