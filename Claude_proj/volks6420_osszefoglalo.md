# Volks 6420 modem – diagnosztika C128 BASIC 7.0-ból

*Összefoglaló, 2026-11-14. Kapcsolódó fájlok: `volks6420_c128_diagnosztika.pdf`, `volks6420.d64`.*

## 1. Kiinduló helyzet

- **Cél:** Commodore 128-cal (BASIC 7.0) kideríteni, működik-e egy Anchor Automation Volks 6420 user port modem.
- **Vonal:** saját FreePBX/Asterisk, rajta egy **Grandstream HT802 V2** ATA, amelyen be van kapcsolva az impulzusos tárcsázás.

## 2. Tények és feltevések

| Állítás | Státusz |
|---|---|
| Az Anchor Automation gyártotta kb. 1985-ben, C64/C128-hoz | **Tény** (CHM, CatalogIt) |
| **Nem Hayes-modem**: nincs `AT` → `OK` teszt, a gép a user port vonalain vezérli közvetlenül | **Tény** (az 1200-as Volksmodemre dokumentált), a 6420-ra **következtetés** |
| A 6420/6470/6480 közös kézikönyve nem írja le a vezérlő protokollt | **Tény** (VCFed fórum) |
| Az 1200-as Volksmodem interfésze eltér a CBM-„szabványtól”, nincs rajta kapcsoló, az off-hookot és a sebességet a hardverinterfész vezérli | **Tény** (Usenet, comp.sys.cbm) |
| A 6420 300 baudos, Bell 103 | **Feltevés** (gyenge forrás) |
| A 6420 bitkiosztása megegyezik az 1650-esével | **Nem ismert**, ez a munkahipotézis |
| Az ilyen modemek szoftverei nem figyelik a vonalhangot, vakon tárcsáznak (off-hook → kb. 2 s várakozás → tárcsázás) | **Tény** az 1650-re és a C128 kézikönyvre, a 6420-ra **következtetés** |
| Az HT802 V2 támogatja az impulzusos tárcsázást, 2 REN/port, van beépített GR-909 vonalteszt | **Tény** (Grandstream dokumentáció) |
| Az SPA112 nem támogatja az impulzusos tárcsázást | **Gyenge forrás** (vásárlói Q&A) |

### Commodore 1650 user port kiosztás (referencia)

| Tű | Jel | Funkció |
|---|---|---|
| B+C | FLAG2+PB0 | RXD |
| D | PB1 | RTS |
| E | PB2 | DTR |
| F | PB3 | RI (csengetés) |
| H | PB4 | DCD (vivőjel), 0 = van carrier |
| J | PB5 | HOOK, 0 V = off-hook; impulzusos tárcsázáshoz is ez kell |
| K | PB6 | CTS |
| L | PB7 | DSR |
| M | PA2 | TXD |

- **Port B adatregiszter:** `56577` ($DD01)
- **Port B irányregiszter (DDR):** `56579` ($DD03)
- **Bell 103 frekvenciák:** originate 1070/1270 Hz, answer 2025/2225 Hz.

## 3. Diagnosztikai sorrend

0. **Szemrevételezés:** kövesd a user port vonalait a modem-IC-ig. A chip datasheetje adja a biztos bitkiosztást.
1. **PORTMON:** mérd meg a nyugalmi állapotot modemmel és modem nélkül. Ha egy bit modemmel 0, modem nélkül 1, akkor azt a modem hajtja (az ő kimenete). **Ezt a bitet soha ne kapcsold kimenetre.**
2. **HOOKTEST:** a PB5-öt billegteti. Figyelj a relé kattanására, és mérd a vonalat: on-hook állapotban néhány tíz volt / szakadás, off-hook állapotban néhány volt / néhány száz ohm.
3. **TXTEST:** 300 baud, 8N1, folyamatosan 'U' karaktereket küld. Off-hook állapotban futtasd.
4. **Teljes lánc:** a modemet egy softmodem hívja. Két út van:
   - **Hotline:** az ATA felvételkor automatikusan tárcsáz. SPA112-n `( S0 <:700> )`, ez a szintaxis **emlékből** van, nem ellenőriztem. Így a tárcsázás teljesen kimarad.
   - **Impulzusos tárcsázás:** a PULSE programmal, az HT802 V2-n.
   - **A túloldal:** Asterisk `app_softmodem` (V.21/V.23/Bell 103/V.22). Spandsp-vel kell fordítani, a megbízhatósága vegyes.
   - **Siker jele:** a PORTMON-ban a PB4 (DCD) bit változik, a TXTEST fogad karaktereket.
5. **Alternatíva:** az eredeti 6420-as szoftverlemez, ha meglesz. Logikai analizátorral a user porton a saját protokollja is visszafejthető.

> **Kockázat:** ha a modem egyik kimenetét a gép is meghajtja, a két kimenet egymás ellen dolgozik, és a CIA vagy a modem sérülhet. Teszteléshez használj user port breakoutot, és minden vonalra tegyél 330 Ω – 1 kΩ soros ellenállást. A modemet csak kikapcsolt gépnél dugd be vagy húzd ki.

## 4. Elektromos ellenőrzések (HT802 V2)

- **GR-909 vonalteszt** az ATA webes felületén, rádugott modemmel. Vizsgál idegen feszültséget, REN-terhelést, rövidzárat és szakadást.
- **Hurokáram:** árammérő sorba kötve, a HOOKTEST off-hook fázisában. Tipikusan kb. 20–30 mA kellene (általános érték, a HT802-re nincs adat).
- **ATA-beállítások** (emlékből, ellenőrizendő):
  - ha van „Pulse Dialing Standard”, az álljon *General*-on (ne Swedish vagy NZ);
  - SLIC/impedancia: USA / 600 Ω.
- **Csengetőfeszültség:** nem ismert. Ha az automatikus hívásfogadás nem működik, ezt gyanítsd elsőként.
- **Hibakeresés az Asterisk oldalon:** `asterisk -rvvv`, ott látszik, milyen számra jött hívás az ATA-tól.

## 5. Programok

Mind C128 módra szól; a BANK és a SLEEP utasítás C64 módban nem létezik. Betöltés: `DLOAD"NÉV"`, majd `RUN`. A begépeléshez nagybetű/grafika módban SHIFT nélkül üss.

### PORTMON – a port B bitjeinek változásait írja ki

```basic
10 BANK 15:POKE 56579,0
20 PRINT "PB 76543210 = L K J H F E D C"
30 O=-1
40 V=PEEK(56577):IF V=O THEN 40
50 S$="":M=128
60 FOR B=7 TO 0 STEP -1
62 S$=S$+CHR$(48-((V AND M)>0))
64 M=M/2:NEXT
70 PRINT TI$;" ";S$;" ";V
80 O=V:GOTO 40
```

Az `M=M/2` szándékos: a CBM BASIC `2^B` számítása pontatlan, az `AND` pedig csonkít.

### HOOKTEST – 2 másodpercenként off-hook / on-hook a PB5-ön

```basic
10 BANK 15
20 POKE 56577,PEEK(56577) OR 32
30 POKE 56579,PEEK(56579) OR 32
40 PRINT "OFF HOOK"
45 POKE 56577,PEEK(56577) AND 223
50 SLEEP 2
60 PRINT "ON HOOK"
65 POKE 56577,PEEK(56577) OR 32
70 SLEEP 2:GOTO 40
```

- **Leállítás:** RUN/STOP, utána `POKE 56579,0`.
- **Másik bit kipróbálása:** a 20, 30, 45 és 65-ös sorban a `32` helyére 2, 4, 8, 16, 64 vagy 128 kerül, az `AND 223` helyére pedig 255 mínusz az adott bit értéke. A PB0-t és a PORTMON-ban modemkimenetnek talált biteket hagyd ki.

### TXTEST – RS-232 küldés és fogadás 300 baudon, bármely billentyű = vége

```basic
10 OPEN 2,2,0,CHR$(6)+CHR$(0)
20 PRINT#2,"UUUUUUUUUUUUUUUU";
30 GET#2,A$:IF A$<>"" THEN PRINT A$;
40 GET A$:IF A$="" THEN 20
50 CLOSE 2
```

### PULSE – impulzusos tárcsázó, CIA2 Timer A-val időzítve

```basic
10 BANK 15:POKE 56589,127
20 CL=985248:REM PAL. NTSC=1022727
30 BR=60:MK=40:ID=800:REM MS
40 POKE 56577,PEEK(56577) OR 32
50 POKE 56579,PEEK(56579) OR 32
60 INPUT "NUMBER";N$
70 GOSUB 500:PRINT "OFF HOOK, WAIT 2S"
80 T=2000:GOSUB 400
90 FOR I=1 TO LEN(N$)
100 A$=MID$(N$,I,1):IF A$<"0" OR A$>"9" THEN 150
105 D=VAL(A$):IF D=0 THEN D=10
110 FOR P=1 TO D
120 GOSUB 600:T=BR:GOSUB 400
130 GOSUB 500:T=MK:GOSUB 400
140 NEXT P
150 T=ID:GOSUB 400:NEXT I
160 PRINT "DIALED. ANY KEY = HANG UP"
170 GET K$:IF K$="" THEN 170
180 GOSUB 600:POKE 56579,PEEK(56579) AND 223:END
400 C=INT(T*CL/1000)
410 IF C>65000 THEN X=65000:C=C-65000:GOSUB 450:GOTO 410
420 X=C:GOSUB 450:RETURN
450 H=INT(X/256):POKE 56580,X-H*256:POKE 56581,H
455 Z=PEEK(56589)
460 POKE 56590,25
470 IF (PEEK(56589) AND 1)=0 THEN 470
480 RETURN
500 POKE 56577,PEEK(56577) AND 223:RETURN
600 POKE 56577,PEEK(56577) OR 32:RETURN
```

- **Mit csinál:** bekér egy számot, off-hook állapotba megy, vár 2 másodpercet, majd impulzusokkal tárcsáz: 60 ms bontás, 40 ms zárás, a számjegyek között 800 ms. Billentyűnyomásra leteszi a vonalat. A nem számjegy karaktereket kihagyja.
- **Időzítés:** a CIA2 hardveres timerével megy, így független a C128 megszakítás-frekvenciájától.
- **NTSC gép esetén:** a 20-as sorban `CL=1022727`. PAL gépnél (Svájc) nincs teendő.
- **Valós időzítés:** a BASIC futási ideje miatt minden szakasz várhatóan pár ms-mal hosszabb (becslés). Ha az ATA rosszul érti a számjegyeket, csökkentsd a `BR`/`MK` értéket, például 55/35-re.
- **Előfeltétel:** csak akkor használd, ha a HOOKTEST már igazolta, hogy a hook-relé a PB5-re reagál.

## 6. Állapot (2026-11-14)

- A `volks6420.d64` négy programot tartalmaz: PORTMON, HOOKTEST, TXTEST, PULSE. A lemezt visszaolvasással ellenőriztem, valódi C128-on még nem futtattam.
- A HOOKTEST futtatása közben nem látszott változás. Ez nyitott kérdés: lehet, hogy rossz bitet vezérelünk, hiányzik a táp, vagy rosszul érintkezik a csatlakozó.
- **Következő lépések:**
  - PORTMON-értékek felírása modemmel és modem nélkül;
  - feszültség és áram mérése a vonalon HOOKTEST közben;
  - a 9 V AC táp ellenőrzése a user port 10-es és 11-es tűje között;
  - az élcsatlakozó megtisztítása.

## Források

- CatalogIt – Volks 6420: https://hub.catalogit.app/vintagecomputer.gallery/folder/entry/1206ffd0-a157-11ef-9750-ff6bb693fba6
- Computer History Museum – Volks 6420: https://www.computerhistory.org/collections/catalog/102674043
- VCFed – Volks 6470/6480 manual: https://forum.vcfed.org/index.php?threads/volks-modem-6470-6480-manual-or-other-docs.74928/
- comp.sys.cbm – Volksmodem review: https://utzoo.superglobalmegacorp.com/usenet/news048f1/b68/comp/sys/cbm/22.txt
- 1650 AUTOMODEM specs: https://www.c128.ca/cbm/64-128/misc/1650spec.txt
- C128 System Guide – modem programming: https://www.manualslib.com/manual/862628/Commodore-128.html?page=115
- commodore-128.org – modem peeks & pokes: https://www.commodore-128.org/index.php?msg=155
- Grandstream HT8xx FAQ: https://documentation.grandstream.com/knowledge-base/ht8xx-v1-faq/
- Grandstream HT80x V2 Admin Guide: https://documentation.grandstream.com/wp-content/uploads/2026/10/HT80x-V2-–-Administration-Guide.pdf
- osmocom – Software Modems (app_softmodem): https://osmocom.org/projects/retro-bbs/wiki/Software_Modems
