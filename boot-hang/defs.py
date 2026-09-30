import re,sys
def defs(p):
    d={}
    for l in open(p,encoding='utf-8',errors='replace'):
        m=re.match(r'\s*#define\s+(\w+)(?:\s+(.*?))?\s*(//.*)?$',l.rstrip('\n'))
        if m: d.setdefault(m.group(1),[]).append((m.group(2) or '').strip())
    return d
for f in ('Configuration.h','Configuration_adv.h'):
    a=defs('stock_'+f); b=defs('dec_merged_'+f)
    print('=====',f)
    for k in sorted(set(a)|set(b)):
        if a.get(k)!=b.get(k):
            print(f"  {k:32s} stock={a.get(k)}  user={b.get(k)}")
