<div align="center">

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=28&duration=700&pause=1000&color=E8423F&center=true&vCenter=true&repeat=false&width=500&height=35&lines=Strikes+Captured" alt="Typing SVG" /></a>

</div>

# Strikes Captured — FORENSIC · 🟡 AVERAGE

- **Status:** ✅ RESOLVIDO — texto digitado reconstruído a partir dos reports HID de 8 bytes do teclado
- **Pontos:** 125
- **Anexo / Alvo:** `frappes.pcap` (pcap usbmon, `usb-linux-mmap`, 86 pacotes, 7 592 bytes, SHA256 `5b32608b74534c0c8ac4df9028305d0bad568b01904c9c33b08fead505d6860b`) + `README.txt` (que só repete o enunciado em francês)
- **Enunciado:** *"USB capture of a keyboard connected to a workstation. Reconstruct what was typed."*
- **Flag:** `CyberZerk{usb_h1d_k3yb0ard_r3p0rt_8_0ct3ts}`

---

## TL;DR

1. A captura usbmon tem 86 `URB_INTERRUPT in`, todos de um único dispositivo (`1.5.1`), o teclado. Os 8 bytes de cada report estão em `usb.capdata`.
2. Cada report HID de teclado é `[modifier][reserved][k1..k6]`. Um report com tecla é sempre seguido de um report zerado, que é a tecla sendo solta.
3. Traduzindo os *usage IDs* pela tabela HID em layout US e aplicando o Shift quando o modifier vale `0x02`, sai a flag. O [`solve.py`](solve.py) automatiza isso.

## Análise

### 1. Visão geral da captura

```bash
file frappes.pcap      # "Memory-mapped Linux USB" -> usbmon (equivalente Linux do USBPcap)
capinfos frappes.pcap  # 86 pacotes, encapsulamento 115 (usb-linux-mmap), duração 0 s
tshark -r frappes.pcap -T fields -e frame.number -e usb.src -e usb.capdata -e usbhid.data | head
```

```
1    1.5.1    0200060000000000
2    1.5.1    0000000000000000
3    1.5.1    00001c0000000000
4    1.5.1    0000000000000000
```

- **Um único dispositivo** (`1.5.1`), sem mouse nem outros aparelhos misturados.
- **`usbhid.data` vazio:** a captura não tem a enumeração do dispositivo (os descritores), então o Wireshark não reconhece o tráfego como HID e os bytes ficam no campo genérico `usb.capdata`.
- Todos os timestamps são idênticos (duração 0 s), o que indica uma captura gerada sinteticamente.

### 2. Anatomia do report HID de teclado (boot protocol)

```
byte:   0          1         2    3    4    5    6    7
      [modifier] [reserved] [k1] [k2] [k3] [k4] [k5] [k6]
```

- **Modifier (byte 0):** um bit por modificadora. `0x01` é o Ctrl esquerdo, `0x02` o **Shift esquerdo** e `0x20` o Shift direito.
- **k1 a k6:** *usage IDs* (HID Usage Tables, página *Keyboard/Keypad* `0x07`) das até 6 teclas pressionadas naquele instante. **Não são ASCII.**
- **Report zerado:** nenhuma tecla pressionada. Por isso os pacotes alternam entre tecla e zerado (pressionar, soltar).

| Usage ID | Tecla | Com Shift |
|---|---|---|
| `0x04` → `0x1d` | `a` → `z` | A–Z |
| `0x1e` → `0x26` | `1` → `9` | `! @ # $ % ^ & * (` |
| `0x27` | `0` | `)` |
| `0x28` / `0x2a` / `0x2c` | Enter / Backspace / Espaço | |
| `0x2d` | `-` | `_` |
| `0x2f` / `0x30` | `[` / `]` | `{` / `}` |

Decodificando à mão os primeiros reports: `02 00 06` é Shift + `0x06` (c), que dá **C**. Depois vêm `1c` (y), `05` (b), `08` (e) e `15` (r), e em seguida `02 00 1d`, Shift + z, que dá **Z**. O começo é `CyberZerk{`.

### 3. Layout: QWERTY ou AZERTY?

A Tricatel é francesa, então o teclado podia ser AZERTY. O usage ID representa a **posição física** da tecla segundo o layout US, não a letra impressa nela: no AZERTY, a posição `0x1d` é `w`. Como os primeiros reports formam `CyberZerk` (e não `CyberWerk`), a leitura em layout US está confirmada pelo próprio formato da flag.

### 4. Decodificação automatizada

Decodificar 43 reports à mão é lento e fácil de errar. O [`solve.py`](solve.py) faz o seguinte:

1. extrai `frame.number` e `usb.capdata` com o `tshark`;
2. para cada report, considera só as teclas **recém-pressionadas** (o conjunto atual menos o anterior), para que uma tecla segurada por vários reports não vire várias letras;
3. aplica o Shift (`modifier & 0x22`) e trata o Backspace (`0x2a`), apagando o caractere anterior;
4. imprime o progresso ao vivo, frame a frame, com o texto acumulado.

```bash
python3 -I solve.py frappes.pcap
```

```
frame    1  0200060000000000  mod=0x02 key=0x06 -> 'C'   | C
frame    3  00001c0000000000  mod=0x00 key=0x1c -> 'y'   | Cy
...
frame   69  0000250000000000  mod=0x00 key=0x25 -> '8'   | CyberZerk{usb_h1d_k3yb0ard_r3p0rt_8
...
frame   85  0200300000000000  mod=0x02 key=0x30 -> '}'   | CyberZerk{usb_h1d_k3yb0ard_r3p0rt_8_0ct3ts}

Texto reconstruído:
CyberZerk{usb_h1d_k3yb0ard_r3p0rt_8_0ct3ts}
```

A flag descreve o próprio mecanismo: *"USB HID keyboard report: 8 octets"*. *Octet* é como os franceses (e as RFCs) chamam o byte.

## O que não funcionou

| Hipótese | Resultado | Por quê |
|---|---|---|
| Ler os dados em `usbhid.data` | ✗ (vazio) | Sem os descritores do dispositivo, o Wireshark não dissecou o tráfego como HID; os bytes estavam no `usb.capdata` |
| Teclado AZERTY (máquina francesa) | ✗ (falsificada) | Com AZERTY, `0x1d` seria `w` e daria `CyberWerk`; o formato da flag confirma o layout US |
| Pegadinha com Backspace (`0x2a`) ou teclas simultâneas | ✗ (não havia) | Nenhum report teve `0x2a` nem mais de um keycode; o texto foi digitado direto |

## Conclusão

Forense de USB HID: identificar o dispositivo e o campo com os bytes (`usb.capdata`), entender o formato do report de 8 bytes (modifier mais 6 *usage IDs*), confirmar o layout e traduzir. A decodificação manual dos primeiros reports serve para validar o modelo; o `solve.py` faz o resto.

---

## Apêndice — ferramentas

- `file` / `capinfos frappes.pcap`: identificam o formato usbmon e o tamanho da captura.
- `tshark -r frappes.pcap -T fields -e frame.number -e usb.src -e usb.capdata`: lista os reports por dispositivo.
- `tshark ... | grep -v '0000000000000000$'`: esconde os reports de tecla solta.
- [`solve.py`](solve.py): decodificador HID (layout US, Shift, Backspace, só teclas recém-pressionadas).
- Alternativa pronta: [`ctf-usb-keyboard-parser`](https://github.com/TeamRocketIST/ctf-usb-keyboard-parser).
- Referência: *HID Usage Tables*, USB-IF, seção 10 (*Keyboard/Keypad Page 0x07*).
