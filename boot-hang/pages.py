import sys,subprocess,re
P='/home/ken/.platformio/packages/toolchain-gccarmnoneeabi@1.90201.191206/bin/arm-none-eabi-nm'
def pages(E,pat):
    ps={}
    for l in subprocess.check_output([P,'-S','-C',E]).decode().splitlines():
        p=l.split(None,3)
        if len(p)==4 and p[2] in 'tTwWrR' and re.search(pat,p[3]):
            a=int(p[0],16)&~1; s=int(p[1],16)
            for pg in range(a//2048, (a+s-1)//2048+1): ps.setdefault(pg,[]).append(p[3][:40])
    return ps
pat=r'DWIN|Dwin|dwin|USART3|init_lcd|MarlinUI::init\(|Encoder|HMI_|LCD_SERIAL|MSerial3|uart_attach|UART_IT|serial_tx|serial_rx'
res={}
for arg in sys.argv[1:]:
    tag,E=arg.split('=',1); res[tag]=pages(E,pat)
for tag,ps in res.items():
    print(tag, 'pages(abs 0x08xxxxxx/2K):', ' '.join(f"{(p*2048):08x}" for p in sorted(ps)))
