#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════╗
║          IP NETWORK TOOLS v1.0                  ║
║  Cross-platform: Linux | Windows | Termux       ║
╚══════════════════════════════════════════════════╝
Author  : IP Tools CLI
Support : Linux, Windows, Android (Termux)
Usage   : python ip_tools.py  OR  python3 ip_tools.py
"""

import os
import sys

# ─── UTILS ────────────────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def sep(char='─', n=58):
    print(' ' + char * n)

def sep2(n=58):
    print(' ' + '═' * n)

def pause():
    input('\n  [Tekan Enter untuk kembali ke menu...]')

# ─── KONVERSI DASAR ───────────────────────────────────────────────────────────

def octet_to_bin(octet: int) -> str:
    """Integer 0-255 → string biner 8 bit"""
    return format(octet, '08b')

def ip_to_int(ip: str) -> int:
    """IP string → integer 32-bit"""
    parts = list(map(int, ip.split('.')))
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

def int_to_ip(n: int) -> str:
    """Integer 32-bit → IP string"""
    return f"{(n >> 24) & 0xFF}.{(n >> 16) & 0xFF}.{(n >> 8) & 0xFF}.{n & 0xFF}"

def ip_to_bin_str(ip: str) -> str:
    """IP decimal → biner dengan titik  ex: 11000000.10101000.00000001.00000001"""
    return '.'.join(octet_to_bin(int(o)) for o in ip.split('.'))

def bin_str_to_ip(b: str) -> str:
    """Biner (dengan/tanpa titik) → IP decimal"""
    clean = b.replace('.', '').replace(' ', '')
    if len(clean) != 32 or not all(c in '01' for c in clean):
        raise ValueError("Format biner tidak valid")
    parts = [clean[i:i+8] for i in range(0, 32, 8)]
    return '.'.join(str(int(p, 2)) for p in parts)

def prefix_to_mask_int(prefix: int) -> int:
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF

# ─── VALIDASI INPUT ───────────────────────────────────────────────────────────

def validate_ip(ip: str) -> bool:
    try:
        parts = ip.strip().split('.')
        if len(parts) != 4:
            return False
        return all(0 <= int(p) <= 255 for p in parts)
    except:
        return False

def validate_prefix(prefix: int) -> bool:
    return 0 <= prefix <= 32

def parse_cidr(cidr: str):
    """Parse 'x.x.x.x/xx' → (ip_str, prefix_int)"""
    if '/' not in cidr:
        raise ValueError("Format harus x.x.x.x/prefix")
    ip, pfx = cidr.strip().split('/')
    prefix = int(pfx)
    if not validate_ip(ip):
        raise ValueError("IP tidak valid")
    if not validate_prefix(prefix):
        raise ValueError("Prefix harus 0–32")
    return ip.strip(), prefix

# ─── PERHITUNGAN SUBNET ───────────────────────────────────────────────────────

def calculate_subnet(ip: str, prefix: int) -> dict:
    mask_int    = prefix_to_mask_int(prefix)
    ip_int      = ip_to_int(ip)
    network_int = ip_int & mask_int
    bcast_int   = network_int | (~mask_int & 0xFFFFFFFF)
    gw_int      = network_int + 1
    last_int    = bcast_int - 1
    total_host  = max(0, bcast_int - network_int - 1)
    block_size  = 2 ** (32 - prefix)

    return {
        'ip'         : ip,
        'prefix'     : prefix,
        'mask'       : int_to_ip(mask_int),
        'network'    : int_to_ip(network_int),
        'gateway'    : int_to_ip(gw_int),
        'dns1'       : int_to_ip(gw_int),          # biasanya sama dgn gateway
        'dns2'       : int_to_ip(gw_int + 1),      # alternatif DNS
        'host_first' : int_to_ip(gw_int),
        'host_last'  : int_to_ip(last_int),
        'broadcast'  : int_to_ip(bcast_int),
        'total_host' : total_host,
        'block_size' : block_size,
    }

# ─── DISPLAY ─────────────────────────────────────────────────────────────────

def label(text, width=22):
    return f"  {text:<{width}}"

def row(lbl, val_dec, val_bin=None):
    if val_bin:
        print(f"{label(lbl)}: {val_dec}")
        print(f"{label('')}  {val_bin}")
    else:
        print(f"{label(lbl)}: {val_dec}")

def print_subnet_result(r: dict):
    sep2()
    print('  ║  📊  HASIL SUBNET CALCULATOR')
    sep2()

    # ── DECIMAL ──
    print('\n  [ DECIMAL ]\n')
    row('IP Input',            r['ip'])
    row('Prefix',              f"/{r['prefix']}")
    row('Subnet Mask',         r['mask'])
    row('Network Address',     r['network'])
    row('Default Gateway',     r['gateway'])
    row('DNS 1 (opsional)',    r['dns1'])
    row('DNS 2 (opsional)',    r['dns2'])
    row('Host Pertama',        r['host_first'])
    row('Host Terakhir',       r['host_last'])
    row('Broadcast Address',   r['broadcast'])
    row('Total Host Usable',   str(r['total_host']))
    row('Block Size',          str(r['block_size']))

    sep()

    # ── BINARY ──
    print('\n  [ BINARY ]\n')
    fields_bin = [
        ('IP Input',          r['ip']),
        ('Subnet Mask',       r['mask']),
        ('Network Address',   r['network']),
        ('Default Gateway',   r['gateway']),
        ('Broadcast Address', r['broadcast']),
    ]
    for lbl, val in fields_bin:
        print(f"  {lbl:<22}: {val}")
        print(f"  {'':<22}  {ip_to_bin_str(val)}")
        print()

    sep2()

def print_dec_to_bin_result(ip: str):
    sep2()
    print('  ║  🔢  DECIMAL → BINARY')
    sep2()
    print(f"\n  IP Decimal : {ip}")
    print(f"  IP Binary  : {ip_to_bin_str(ip)}")
    sep()
    print('\n  [ Per Oktet ]\n')
    for i, o in enumerate(ip.split('.'), 1):
        print(f"  Oktet {i}  |  {int(o):>3}  →  {octet_to_bin(int(o))}")
    sep2()

def print_bin_to_dec_result(b_input: str):
    ip = bin_str_to_ip(b_input)
    clean = b_input.replace('.', '').replace(' ', '')
    parts = [clean[i:i+8] for i in range(0, 32, 8)]
    formatted = '.'.join(parts)

    sep2()
    print('  ║  🔢  BINARY → DECIMAL')
    sep2()
    print(f"\n  IP Binary  : {formatted}")
    print(f"  IP Decimal : {ip}")
    sep()
    print('\n  [ Per Oktet ]\n')
    for i, p in enumerate(parts, 1):
        print(f"  Oktet {i}  |  {p}  →  {int(p, 2)}")
    sep2()

# ─── MENU ─────────────────────────────────────────────────────────────────────

def menu_subnet():
    clear()
    sep2()
    print('  ║  🌐  SUBNET CALCULATOR')
    sep2()
    print('\n  Format  : x.x.x.x/prefix')
    print('  Contoh  : 192.168.1.0/24')
    print('            10.11.11.0/26')
    print('            172.16.0.0/20\n')

    cidr = input('  Masukkan IP/Prefix : ').strip()
    try:
        ip, prefix = parse_cidr(cidr)
        result = calculate_subnet(ip, prefix)
        print()
        print_subnet_result(result)
    except ValueError as e:
        print(f'\n  ❌  Error: {e}')
    except Exception:
        print('\n  ❌  Input tidak valid! Cek format.')

    pause()

def menu_dec_to_bin():
    clear()
    sep2()
    print('  ║  🔢  DECIMAL → BINARY')
    sep2()
    print('\n  Contoh : 192.168.1.1')
    print('           10.0.0.1\n')

    ip = input('  Masukkan IP Decimal : ').strip()
    if not validate_ip(ip):
        print('\n  ❌  IP tidak valid! Format: x.x.x.x (0–255 tiap oktet)')
    else:
        print()
        print_dec_to_bin_result(ip)

    pause()

def menu_bin_to_dec():
    clear()
    sep2()
    print('  ║  🔢  BINARY → DECIMAL')
    sep2()
    print('\n  Format bisa pakai titik atau tidak:')
    print('  Contoh : 11000000.10101000.00000001.00000001')
    print('           11000000101010000000000100000001\n')

    b = input('  Masukkan IP Binary : ').strip()
    try:
        print()
        print_bin_to_dec_result(b)
    except ValueError as e:
        print(f'\n  ❌  Error: {e}')
    except:
        print('\n  ❌  Input tidak valid! Pastikan 32 bit (hanya angka 0 dan 1).')

    pause()

def menu_batch():
    """Hitung beberapa subnet sekaligus"""
    clear()
    sep2()
    print('  ║  📋  BATCH SUBNET CALCULATOR')
    sep2()
    print('\n  Masukkan beberapa IP/Prefix (satu per baris)')
    print('  Ketik "done" jika sudah selesai\n')

    entries = []
    while True:
        line = input(f'  [{len(entries)+1}] IP/Prefix : ').strip()
        if line.lower() in ('done', 'selesai', ''):
            break
        entries.append(line)

    if not entries:
        print('\n  Tidak ada input.')
        pause()
        return

    print()
    sep2()
    print('  ║  HASIL BATCH')
    sep2()

    for e in entries:
        try:
            ip, prefix = parse_cidr(e)
            r = calculate_subnet(ip, prefix)
            print(f'\n  ► {e}')
            sep()
            print(f"  Network   : {r['network']}")
            print(f"  Mask      : {r['mask']}")
            print(f"  Gateway   : {r['gateway']}")
            print(f"  Broadcast : {r['broadcast']}")
            print(f"  Host      : {r['host_first']} – {r['host_last']}  ({r['total_host']} host)")
        except Exception as ex:
            print(f'\n  ► {e}  ❌  {ex}')

    sep2()
    pause()

# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    while True:
        clear()
        print()
        sep2()
        print('  ║                                                        ║')
        print('  ║          🌐  IP NETWORK TOOLS  v1.0                   ║')
        print('  ║       Linux │ Windows │ Android (Termux)               ║')
        print('  ║                                                        ║')
        sep2()
        print()
        print('  [1]  Subnet Calculator          (IP, Mask, Gateway, dll)')
        print('  [2]  IP Decimal  →  Binary')
        print('  [3]  IP Binary   →  Decimal')
        print('  [4]  Batch Subnet (banyak IP sekaligus)')
        print()
        sep()
        print('  [0]  Keluar')
        sep()
        print()

        choice = input('  Pilih menu [0-4] : ').strip()

        if   choice == '1': menu_subnet()
        elif choice == '2': menu_dec_to_bin()
        elif choice == '3': menu_bin_to_dec()
        elif choice == '4': menu_batch()
        elif choice == '0':
            print('\n  Sampai jumpa! 👋\n')
            sys.exit(0)
        else:
            print('\n  ❌  Pilihan tidak ada, coba lagi.')
            pause()

if __name__ == '__main__':
    main()
