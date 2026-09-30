import sys,re,hashlib,subprocess
OD='/home/ken/.platformio/packages/toolchain-gccarmnoneeabi@1.90201.191206/bin/arm-none-eabi-objdump'
def funcs(elf):
    out=subprocess.check_output([OD,'-d','--no-show-raw-insn','-C',elf]).decode(errors='replace')
    d={};cur=None;buf=[]
    for l in out.splitlines():
        m=re.match(r'^[0-9a-f]+ <(.*)>:$',l)
        if m:
            if cur: d.setdefault(cur,[]).append('\n'.join(buf))
            cur=m.group(1);buf=[];continue
        if cur and re.match(r'^ *[0-9a-f]+:\t',l):
            s=l.split(':',1)[1].strip()
            s=re.sub(r'<[^>]*\+0x[0-9a-f]+>','',s); s=re.sub(r'\b(0x)?[0-9a-f]{7,8}\b','ADDR',s); s=re.sub(r'[;].*$','',s)
            s=re.sub(r'\[pc, #\d+\]','[pc]',s); s=re.sub(r'(b\w*(\.n|\.w)?)\s+\S+','\\1',s) if re.match(r'b(eq|ne|cs|cc|mi|pl|vs|vc|hi|ls|ge|lt|gt|le|al)?(\.n|\.w)?\s',s) else s
            buf.append(s)
    if cur: d.setdefault(cur,[]).append('\n'.join(buf))
    return {k:hashlib.md5('\n##\n'.join(sorted(v)).encode()).hexdigest() for k,v in d.items()}
a=funcs(sys.argv[1]); b=funcs(sys.argv[2])
diff=[k for k in a if k in b and a[k]!=b[k]]; only_a=[k for k in a if k not in b]; only_b=[k for k in b if k not in a]
print(f"funcs a={len(a)} b={len(b)} changed={len(diff)} only_a={len(only_a)} only_b={len(only_b)}")
for k in sorted(diff): print("CHANGED",k)
for k in sorted(only_a): print("ONLY_A ",k)
for k in sorted(only_b): print("ONLY_B ",k)
