#!/usr/bin/env python3
"""Decodifica reports de teclado USB HID (boot protocol, 8 bytes) de um pcap usbmon."""
import subprocess
import sys

pcap = sys.argv[1] if len(sys.argv) > 1 else "frappes.pcap"

# HID Usage Tables, Keyboard/Keypad page (0x07), layout US: usage -> (normal, shift)
KEYS = {i: (chr(ord("a") + i - 4), chr(ord("A") + i - 4)) for i in range(0x04, 0x1E)}
KEYS.update(zip(range(0x1E, 0x28), zip("1234567890", "!@#$%^&*()")))
KEYS.update({
    0x28: ("\n", "\n"), 0x2B: ("\t", "\t"), 0x2C: (" ", " "),
    0x2D: ("-", "_"), 0x2E: ("=", "+"), 0x2F: ("[", "{"), 0x30: ("]", "}"),
    0x31: ("\\", "|"), 0x33: (";", ":"), 0x34: ("'", '"'), 0x35: ("`", "~"),
    0x36: (",", "<"), 0x37: (".", ">"), 0x38: ("/", "?"),
})
SHIFT = 0x02 | 0x20  # LeftShift | RightShift no byte de modifier
BACKSPACE = 0x2A

out = subprocess.run(
    ["tshark", "-r", pcap, "-T", "fields", "-e", "frame.number", "-e", "usb.capdata"],
    capture_output=True, text=True, check=True,
).stdout

typed, prev = [], set()
for line in out.splitlines():
    parts = line.split()
    if len(parts) != 2 or len(parts[1]) != 16:
        continue
    frame, report = parts[0], bytes.fromhex(parts[1])
    mod, pressed = report[0], {k for k in report[2:] if k}
    for key in sorted(pressed - prev):  # só teclas recém-pressionadas (ignora tecla segurada)
        if key == BACKSPACE:
            removed = typed.pop() if typed else ""
            note = f"<BACKSPACE> apagou {removed!r}"
        elif key in KEYS:
            ch = KEYS[key][1 if mod & SHIFT else 0]
            typed.append(ch)
            note = repr(ch)
        else:
            note = f"<usage 0x{key:02x} não mapeado>"
        print(f"frame {frame:>4}  {report.hex()}  mod=0x{mod:02x} key=0x{key:02x} -> {note:<24} | {''.join(typed)}", flush=True)
    prev = pressed

print("\nTexto reconstruído:\n" + "".join(typed))
