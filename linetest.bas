10 rem volks 6420 line test, 1650 pinout
20 rem pb5=hook (0=off hook), pb4=dcd (0=carrier)
25 rem stock kernal: 1 jiffy = 1/60 s, pal too
30 b=56577:d=56579
40 poke b,peek(b)or32:poke d,peek(d)or32
50 print "on hook. ata led should be steady."
60 input "number (digits only)";n$
70 poke b,peek(b)and223:print "off hook, dial tone..."
80 t=ti+100:gosub 900
90 for i=1 to len(n$):v=val(mid$(n$,i,1)):if v=0 then v=10
100 for p=1 to v
110 poke b,peek(b)or32:t=ti+4:gosub 900
120 poke b,peek(b)and223:t=ti+3:gosub 900
130 next p:t=ti+40:gosub 900:next i
140 print "dialed. dcd (1=carrier), any key ends"
150 get k$:if k$<>"" then 200
160 print -((peek(b)and16)=0);:goto 150
200 poke b,peek(b)or32:print:print "on hook":end
900 if ti<t then 900
910 return
