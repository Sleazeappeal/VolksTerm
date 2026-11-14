# VolksTerm 0.1: C64 OS terminal for the Volks 6420

300 baud, 8N1, PETSCII terminal. Pulse dialing in software. For "dumb" user-port
modems with the Commodore 1650 pinout (Volks 6420 assumed compatible, see Step 1).

## License and credits

VolksTerm (`main.a`, the icon, the bundle files) is Copyright (c) 2026
Sleazy, MIT License: see `LICENSE`. The installed app carries the same
text in `readme.t`, and `about.t` names the author.

- Started with Claude Opus 5.5 on claude.ai (the online client): the
  Volks 6420 diagnosis and the C128 BASIC 7.0 test programs in
  `Claude_proj/` were made there.
- Made with Claude Code: VolksTerm 0.1 (`main.a`, `carhelp.py`,
  `linetest.bas`, the help and readme texts, this README and the `bbs/`
  package) was written with Claude Code 2.1.325 by Anthropic, model Claude
  Opus 5.5. The icon is by Sleazy.
- C64 OS by Greg Nacu, OpCoders Inc. VolksTerm runs on it but contains
  none of it.
- Built with the C64 OS SDK headers from OpCoders' `c64os-dev` (MIT,
  Copyright (c) 2023-2024 OpCoders Inc.), which are not included here;
  `bundleapp.py` from the same repo builds the `.car`.
- Assembled with TMPx by Style. Tested with VICE (GPL). Local copies of
  both live in `tools/`, which is not in the repo except for the VICE
  configuration `tools/vice/volksterm.ini`.
- `bbs/` adapts Synchronet BBS (Copyright Rob Swindell, GPL version 2 or
  later), so the `bbs/` package is GPL-2.0-or-later: see `bbs/NOTICE.txt`
  and `bbs/gpl.txt`. The same screens are also in the
  [synchronet-bbs-modem-dialin](https://github.com/Sleazeappeal/synchronet-bbs-modem-dialin)
  repository (`synchronet/40col/`).

## Files

| File | Purpose |
|---|---|
| `main.a` | App source (TMP/TMPx, C64 OS SDK conventions) |
| `bundle.ini`, `bundleapp.ini` | Build + C64 OS Archive (`.car`) settings for the SDK's `bundleapp.py` |
| `menu.txt` | Menu source, converted to PETSCII `menu.m` by `bundleapp.py` |
| `icon.charset` | App icon: phone handset, "VT", dial pulses (24x24, 9 chars) |
| `readme.txt` | In-app readme (`readme.t` in the `.car`): usage, credits, license |
| `help/` | Help utility pages: `toc.txt` lists the pages, one `<page>.txt` each (ASCII, one paragraph per line) |
| `carhelp.py` | Adds `help/` to the `.car` as a subfolder (bundleapp cannot) |
| `LICENSE` | MIT license of VolksTerm |
| `linetest.bas` | BASIC hardware test: hook, pulse dial, DCD |
| `bbs/` | Synchronet 40-column screens + `install.sh` (see "BBS side"), GPL |
| `Claude_proj/` | Volks 6420 diagnosis on the C128 from the claude.ai start of the project (Hungarian `.md`) and its BASIC 7.0 test programs (`portmon`, `hooktest`, `txtest`, `pulse.prg`). The `pulse.prg` there is a later version with a machine-code pulse routine; the `.md` lists the first, BASIC-only one |

## Step 1: verify the hardware first (plain C64 mode, no C64 OS)

1. Modem TALK/DATA switch → DATA, originate mode.
2. Type in or `petcat -w2 -o linetest.prg -- linetest.bas`, run.
3. Off hook → the Grandstream FXS LED should blink (off-hook/busy).
4. Dial a test extension (e.g. Asterisk echo test). Check that the PBX sees the
   correct digits (`asterisk -rvvv`). If digits are wrong or missing: enable
   pulse dialing on the ATA FXS port, or tune `t_brk`/`t_make`.
5. Dial the softmodem extension and check that DCD goes to 1.

If the hook line doesn't react, the 6420 isn't 1650-compatible on PB5, so stop
and re-map `hookbit` / `dcdbit`.

## Step 2: build

PC (TMPx): the SDK headers come from the official
[OpCoders-Inc/c64os-dev](https://github.com/OpCoders-Inc/c64os-dev) repo (MIT,
ASCII, TMPx paths). They are not part of this repository: copy
`include/v1.09/os` from it to `os/` here (or the version that matches your
C64 OS):

```
git clone https://github.com/OpCoders-Inc/c64os-dev ref/c64os-dev
cp -r ref/c64os-dev/include/v1.09/os os
```

```
tools\tmpx\TMPx_v1.1.0-STYLE\windows-i386\TMPx.exe -i main.a -o main.o
```

Native: import `main.a` into TurboMacroPro as SEQ and change the include back
to `//os/h/:modules.h`.

`tools/` holds TMPx 1.1.0 and VICE 3.10 (`petcat`, `c1541`, `x64sc`).
`ref/` holds read-only clones of the OpCoders-Inc repos used as examples
(`c64os-dev`, `TextViewPlus`, `wic64-driver`).

### Package: C64 OS Archive (`.car`)

The app ships the way the OpCoders examples do (TextViewPlus): as a
C64 OS Archive that C64 OS's own Installer unpacks. From this folder:

```
python ref/c64os-dev/tools/bundleapp/bundleapp.py --final
mv VolksTerm.car dist/
python carhelp.py dist/VolksTerm.car
```

This assembles `main.a` into `dist/main.o` and writes `VolksTerm.car`
(archive v3 with CRC32): folder `VolksTerm` with `main.o`, `menu.m`,
`icon.charset`, `readme.t`, and `about.t`/`msg.t` generated from `app_about`/`app_msg`
in `bundle.ini`. `bundleapp.ini` needs absolute tool paths on Windows
(relative ones with `/` fail in `CreateProcess`). `carhelp.py` then adds the
`help/` subfolder (C64 OS Help opens `<app>/help/toc.t`) and rewrites the CRC.

Install in C64 OS: File Manager → copy `VolksTerm.car` into
`//os/applications/` → double-click it → INSTALLER → EXTRACT.

Don't copy the app folder into the CMD HD image with VICE's `c1541`
(`md:` + `write`). C64 OS mishandled folders made that way (app rejected,
garbled name in File Manager, a delete that didn't stick).

### Test in VICE (C64 OS 1.09 on an emulated CMD HD)

`C64OS_HD.dhd` (not in the repo) is a CMD HD image with C64 OS 1.09.
`tools/vice/volksterm.ini` sets the JiffyDOS kernal and drive ROMs and drive
10 = CMD HD (`CMD HD BOOTROM v280.bin`; the ROMs are user-supplied, in
`tools/vice/.../C64` and `.../DRIVES`). Drive 8 is a host folder (`dist/`),
so C64 OS's File Manager can read the `.car` from it:

```
set C=tools\vice\GTK3VICE-3.10-win64\bin
%C%\x64sc.exe -config tools\vice\volksterm.ini +saveres -drive8type 0 -busdevice8 -fs8 dist -10 C64OS_HD.dhd -keybuf "load\"c64os\",10\nrun\n"
```

Run at 100% speed: no warp, no 200%. Both distort real-time timing (RS-232
link, RTC).

With the user port RS-232 device on its default host device (`com1`), VICE
freezes for a few seconds at every RS-232 line change (OPEN, hook, CLOSE)
while it fails to open `com1` (`CreateFile('com1') failed: 2` in the log).
That is the emulator, not the app.

`volksterm.ini` now points the RS-232 device at `127.0.0.1:2341` (raw TCP,
300 baud). For a BBS behind it, forward a raw-TCP PETSCII endpoint there,
e.g. `ssh -N -L 127.0.0.1:2341:127.0.0.1:2341 <bbs-host>` to a Synchronet
softmodem relay. VICE does not pass the PB5 hook line, so dialing has no
effect in the emulator; only the data path after "connect" is tested.

VICE limits (raw TCP mode, VICE 3.10; real hardware is not affected):

- VICE opens the TCP connection on the first CIA2 port B write with DTR
  active, which C64 OS's boot already does (~9 s after start), not when the
  app dials. So the BBS greeting goes to a C64 that isn't listening yet, and
  if nobody dials for a minute or two the BBS times out the login and closes
  (`RS232NET: Error - EOF` in the log). Dial right after boot.
- Raw mode always reports DCD, even after EOF, so there is no automatic
  hang-up when the BBS drops the line; use C=+X.

App behaviour that comes from this testing:

- Any KERNAL IEC access (C64 OS loading About, Help or another utility) turns
  RS-232 RX off (JiffyDOS KERNAL `$ED0E` -> `$F0A4` clears `ENABL` `$02A1`);
  only an RS-232 CHKIN turns it back on. `poll` checks `ENABL & $12` and
  calls `rsrxon` (CHKIN + CLRCHN) when it is 0. Bytes that arrive during the
  load are lost.
- `flushrx` runs once when dialing ends, not at CONNECT: it drops the pulse
  dialing noise but keeps what the BBS sends after the connect.
- PETSCII graphics (screen codes `$40-$7F` in the lowercase set) are drawn
  as ASCII look-alikes (`- | + _ # / \`, solid block = reversed space) via
  `gfxmap`. The C64 OS charsets have no PETSCII graphics: `charset.o`
  holds 96 ASCII-like glyphs (`$40` = `` ` ``, `$5B-$5F` = `{ | } ~` and a
  pattern, `$1C` = `\`, `$1F` = `_`), and `ui.charset` holds 64 UI icons.
  Reverse video (screen code OR `$80`) works.

## BBS side (Synchronet, 40-column callers)

`bbs/` holds 40-column versions of the Synchronet screens that wrap on a
C64, in the same paths as on the BBS host. 80-column callers are not
affected: Synchronet picks `<name>.40col.<ext>` only for 40-column
terminals (and searches `mods/text/menu/` before `text/menu/`), and
`mods/logon.js` changes text strings only when the terminal has fewer than
80 columns.

| File | Screen |
|---|---|
| `text/answer.40col.msg` | Logon screen |
| `mods/text/menu/main.40col.msg` | Main menu (classic shell) |
| `mods/text/menu/logoff.40col.msg` | Log off |
| `mods/text/menu/msgscan.40col.asc` | `?` while reading messages |
| `mods/text/menu/userinfo.40col.msg` | Info → Your statistics |
| `mods/text/menu/textsrch.40col.msg` | `?` at a search prompt |
| `mods/text/menu/batflag.40col.msg` | File listing, batch flagging help |
| `mods/text/menu/tempxfer.40col.asc` | File section → temp directory |
| `mods/text/menu/privchat.40col.asc` | Private chat |
| `mods/text/system.40col.msg` | Info → I → "View system information file" (`../system`) |
| `mods/logonlist.js` | Last callers: one line per caller |
| `mods/logon.js` | New-message scan line, System information (Info → I) |

Each extension matches the stock file (`.asc` vs `.msg`): Synchronet tries
all `.asc` names before any `.msg`, so `msgscan.40col.msg` would lose to
the stock `msgscan.asc`. Synchronet's version and copyright banner (Info → V,
and under System information) is built into Synchronet and still wraps.
Sysop-only screens are left as they are.

Install on the BBS host (copy the `bbs/` folder there first):

```
sudo bash install.sh [--force] [/u00/sbbs]
```

It reads the `mods=` directory from `ctrl/main.ini` and checks that
`exec/logonlist.js` is the version the `mods/` copy was patched from. It
stops before writing anything if a target exists with other content;
`--force` backs such files up as `<file>.bak-<timestamp>` and replaces
them. Running it again only reports `same`. No restart is needed.

## Usage

Type the number, then RETURN (or C=+D) to dial. Any key aborts while dialing.
C=+X hangs up. CTRL+C=+H goes home.

## C64 OS compatibility

Why the KERNAL RS-232 driver: C64 OS has no raw serial API. Its modem drivers
(`up24.zi` etc.) and `network.lib` only carry CNP packets ("Raw bytes of data
are never received or sent through the driver that are not part of a CNP
packet", Networking Guide part I/II). So VolksTerm drives the user port itself.

Verified against c64os.com (Programmer's Guide, Networking Guide, KERNAL ROM
post), 2026-11:

- All KERNAL ROM routines used (SETLFS, SETNAM, OPEN, CLOSE, CHKIN, CHKOUT,
  CHROUT, CLRCHN) are listed as "Compatible". GETIN (deprecated) and CLALL,
  MEMTOP (do not use) are not used. OPEN/CLOSE leave MEMTOP alone because the
  RS-232 buffers are pre-assigned.
- Jiffy = 1/50 s on PAL, 1/60 s on NTSC. The timing constants assume PAL.
- Timer struct (ttime[3] tstat ttrig[2] tvalu[3]), `tintrvl`, `trealtm`
  (trigger runs in the ISR). "Timers are dequeued when an app quits" is true
  only late: `//os/library/loader` clears the queue after it has loaded
  over `$0900`. Until then the timer IRQ runs on whatever now sits where our
  structs were, so `willquit` sets `tcancel` and waits two jiffies.
- Default banking keeps the KERNAL ROM in, BASIC out. C64 OS installs its own
  IRQ/NMI hardware vectors and keeps the NMI RAM vector at `$0318`.
- Layer struct (`slindx` = offset 8), `layerpush`, `markredraw` (X = index).
- `readkcmd`: A = PETSCII, Y = modifier flags. `readkprnt`: A = PETSCII.
- Jump table order init, msgcmd, willquit, freeze, thaw. `menu.m` header
  `Title;<count letter>` (tutorial: `System;a` = 1 item).
- `pgalloc` (carry on error), `pgfree` (Y = page, X = count).

How the app copes with C64 OS banking:

- `$0318` points to `nmiwrap`. It maps I/O + KERNAL ROM in, runs the KERNAL
  RS-232 NMI handler (`$FE47`), then restores `$01`. This protects RX/TX while
  C64 OS or the app has I/O patched out (e.g. to write the color buffer).
- `drawmain` writes the color buffer (RAM under I/O) row by row with IRQs off
  for ~0.6 ms per row. It keeps the KERNAL ROM mapped in (char ROM at `$D000`,
  writes fall through to RAM), so NMIs still reach `nmiwrap` via ROM `$FE43`.

Confirmed from the SDK and OpCoders example sources (`ref/`):

- `scrbuf` = `$0400`, `colbuf` = `$D800` (RAM under I/O), `appbase` = `$0900`
  (`os/s/io.s`, `os/s/app.s`).
- NMIs reach `$0318` with the KERNAL ROM in or out: the C64 OS SwiftLink
  driver wedges `$0318` the same way and notes "KERNAL could be in or out"
  (`ref/wic64-driver/nhd.slxx.zi.asm`). It also saves `$01`, maps I/O + KERNAL
  in and restores `$01`, like `nmiwrap`.
- `$F7-$FA`, `$029B-$029E`, `$02A1` are the RS-232 workspace that C64 OS's own
  user port drivers use (`os/s/io_rs232.t`), so they are free while the
  network driver is set to None.
- Menu messages: X = menu action code (official Hello World tutorial).
  `#switch` preserves A and Y always, X on a match (`os/s/switch.s`).
- `readkcmd`: Y = keymods (`lshftkey` 1, `cbmkey` 2, `ctrlkey` 4, `rshftkey`
  8). Only C= or CTRL turn a key into a menu shortcut, so shifted command keys
  (CRSR up/left) still go to the BBS.
- `menu.m` built from `menu.txt` is byte-identical in format to the tutorial's.
- TMPx `.text` emits PETSCII (`"Vo"` → `$D6 $4F`), which is what `tputs` →
  `pet2scr` expects (checked in `main.lst`, 2026-11-14).
- KERNAL RS-232 OPEN always returns C=1, A=`$F0` ("MEMTOP set", `SEC / LDA
  #$F0 / JMP $FE2D`, at `$F47D` in the JiffyDOS kernal too). BASIC treats `$F0`
  as success, and so does `rsopen` (found with a VICE trace, 2026-11-14).
- Pages from `pgalloc` with `mapapp` are reclaimed by the system on quit;
  TextViewPlus never frees them. Freeing them in `willquit` as well was the
  most likely cause of "Unhandled exception near $c109" on quit.
- From disassembling C64 OS's own modules on the disk (`//os/kernal/*.o`):
  timer structs are 9 bytes and `timeque` only stores a pointer (max 5
  timers; `timeridx` = `$09` is the zero-page count, not a struct offset).
  `quitapp` only sets `loopbrkvec`; the main loop then calls `willquit` in a
  try/catch, loads `//os/library/:loader` and calls it via `jmp ($0900)`.
  C64 OS's NMI vector is `$CE2A: jmp ($0318)`, and its IRQ goes via `$0312`.
- `about.t`: every installed app has a leading space on the version line
  (`" 0.2"`), so `app_about` in `bundle.ini` has one too.

## Test methodology

Before VolksTerm, the modem was examined on the C128 (`Claude_proj/`):
BASIC 7.0 programs PORTMON, HOOKTEST, TXTEST and PULSE, to find out whether
the Volks 6420 follows the 1650 pinout, plus line measurements on the ATA.
Then three stages, each one only after the previous one passed:

1. **Line test on the real machine** (Step 1): `linetest.bas` in plain C64
   mode, without C64 OS. It checks the hook line (PB5), pulse dialing (the
   PBX must see the right digits) and DCD (PB4).
2. **VICE** (see "Test in VICE"): `x64sc` from VICE 3.10 at 100% speed (no
   warp) with `tools/vice/volksterm.ini`: JiffyDOS, C64 OS 1.09 on an
   emulated CMD HD, user-port RS-232 at 300 baud as raw TCP to
   `127.0.0.1:2341`, forwarded with SSH to the PETSCII relay of a test
   Synchronet BBS (never the live one). Checked: login, menus, every
   40-column screen in `bbs/` (by screenshot), About and Help opened while
   online (RX must keep working afterwards), hang-up with C=+X. VICE does
   not pass the hook line, so dialing itself is not tested there.
3. **Real hardware**: install the `.car` with File Manager, dial the BBS
   line through the modem, repeat the stage 2 checks.

Result, 2026-11-14: VolksTerm 0.1 on a Commodore 128 (C64 mode) with a CMD
HD4000 and C64 OS 1.08 (without the 1.09 update) installed from the `.car`
without errors, dialed out, and worked as in the VICE tests. The BBS and its
40-column screens were also checked from the same C128 and Volks 6420 with
TouchTerm 3.9 (Volks 6480 version) and CBterm V6.6, in both C64 and C128
mode. These disks are not in the repo.

## Still unverified (test on the real machine)

- The guide says "you should never draw directly into screen memory". The
  tutorial draws through `setctx`/`ctxdraw` into `scrbuf`/`colbuf`;
  `drawmain` writes those buffers directly. Most likely fine (VIC screen RAM
  is what's meant), but not stated.
- C64 OS drivers have `nhdpause`/`nhdresum` hooks (C64 OS pauses RS-232 NMIs,
  presumably around disk I/O). VolksTerm isn't a driver and gets no such call.
- Logical file 126: no reservation rules documented.

## Known risks / limits

- If RX/TX is dead or garbled but the line test passes, suspect the NMI path
  first (see above).
- Set the C64 OS network driver to None (Network settings, Drvr tab), so no
  driver such as `up24.zi` claims the user port.
- Avoid disk access while online (NMI vs. IEC/JiffyDOS timing).
- While the app runs it owns `$0318`: RUN/STOP+RESTORE triggers the KERNAL
  warm start. C64 OS's own drivers handle it with `quitapp` instead (see
  `chkrstr` in `ref/wic64-driver/nhd.slxx.zi.asm`); not copied yet, because
  telling RESTORE from RS-232 NMIs needs the CIA2 ICR value the KERNAL handler
  reads itself.
- C64 OS background: BBS colors assume a black background.
- `linetest.bas` runs on the stock KERNAL, where 1 jiffy = 1/60 s on PAL too,
  so its pulse timing (4/3 jiffies) differs from the app.
