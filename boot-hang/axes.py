# axes.py SRC DST AXES  -> stock config with UART on the listed axes (e.g. XYE)
import sys
src,dst,axes=sys.argv[1:4]
pin={'X':'PC6','Y':'PC9','Z':'PA13','E':'PA15'}; drv={'X':'X','Y':'Y','Z':'Z','E':'E0'}
s=open(src).read(); lines=""
for ax in axes:
    old=f"#define {drv[ax]}_DRIVER_TYPE TMC2208_STANDALONE\n"; assert s.count(old)==1
    s=s.replace(old,f"#define {drv[ax]}_DRIVER_TYPE TMC2208\n"); lines+=f"#define TMC_UART_PIN_{ax} {pin[ax]}\n"
i=s.index("#define X_DRIVER_TYPE"); s=s[:i]+lines+"\n"+s[i:]
open(dst,'w').write(s)
