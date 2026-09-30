import sys
src,dst,ax=sys.argv[1:4]
pin={'X':'PC6','Y':'PC9','Z':'PA13','E':'PA15'}[ax]
drv={'X':'X','Y':'Y','Z':'Z','E':'E0'}[ax]
s=open(src).read()
old=f"#define {drv}_DRIVER_TYPE TMC2208_STANDALONE\n"; assert s.count(old)==1
s=s.replace(old,f"#define {drv}_DRIVER_TYPE TMC2208\n")
anchor="#define X_DRIVER_TYPE"; i=s.index(anchor)
s=s[:i]+f"#define TMC_UART_PIN_{ax} {pin}\n\n"+s[i:]
open(dst,'w').write(s)
