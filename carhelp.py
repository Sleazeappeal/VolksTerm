#!/usr/bin/env python3
# Copyright (c) 2026 Sleazy. MIT License, see LICENSE.
#
# Adds the help/ folder (C64 OS Help utility: <app>/help/toc.t plus
# one page file per toc line) to the .car made by bundleapp.py,
# which cannot pack subfolders.
#   python carhelp.py dist/VolksTerm.car
# Sources: help/toc.txt and help/<page>.txt, ASCII, one paragraph
# per line. The first line of a page is its title.
import binascii
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HELP = os.path.join(HERE, 'help')
TITLE = b'\xf6\xf1'     # title prefix used by the stock C64 OS help pages


def petscii(text):
    out = bytearray()
    for ch in text.replace('\r\n', '\n'):
        c = ord(ch)
        if ch == '\n':
            out.append(0x0d)
        elif 'a' <= ch <= 'z':
            out.append(c - 0x20)
        elif 'A' <= ch <= 'Z':
            out.append(c + 0x80)
        elif 0x20 <= c < 0x7f:
            out.append(c)
        else:
            sys.exit(f'carhelp: no PETSCII for {ch!r}')
    return bytes(out)


def name16(text):
    n = petscii(text)
    if len(n) > 16:
        sys.exit(f'carhelp: name longer than 16 chars: {text}')
    return n + b'\xa0' * (16 - len(n))


def seq_entry(name, data):
    return b'S\x00' + len(data).to_bytes(3, 'little') + name16(name) + b'\x00' + data


def read(name):
    with open(os.path.join(HELP, name), encoding='ascii') as f:
        return f.read()


def main(car_path):
    car = bytearray(open(car_path, 'rb').read())
    body = car[:-4]
    if binascii.crc32(body).to_bytes(4, 'little') != car[-4:]:
        sys.exit('carhelp: CRC mismatch, not a fresh bundleapp v3 .car?')
    if body[48] != 0x44:
        sys.exit('carhelp: no root directory entry at offset 48')

    toc = read('toc.txt')
    pages = [line for line in toc.splitlines() if line.strip()]
    entries = seq_entry('toc.t', petscii(toc))
    for page in pages:
        data = petscii(read(page + '.txt').strip('\n') + '\n')
        entries += seq_entry(page, TITLE + data)

    count = 1 + len(pages)
    folder = b'D\x00' + count.to_bytes(2, 'little') + b'\x00' + name16('help') + b'\x00'
    root = int.from_bytes(body[50:52], 'little') + 1
    body[50:52] = root.to_bytes(2, 'little')
    body += folder + entries
    out = bytes(body) + binascii.crc32(body).to_bytes(4, 'little')
    open(car_path, 'wb').write(out)
    print(f'carhelp: added help/ ({count} files), {len(out)} bytes')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('usage: carhelp.py <file.car>')
    main(sys.argv[1])
