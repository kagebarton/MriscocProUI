import re,sys
def defs(paths):
    d={}
    for p in paths:
        for line in open(p,errors='replace'):
            m=re.match(r'\s*#define\s+(\w+)(?:\s+(.*?))?\s*(?://.*)?$',line)
            if m:
                k=m.group(1); v=re.sub(r'\s+',' ',(m.group(2) or '').strip())
                d.setdefault(k,set()).add(v)
    return d
a=defs(sys.argv[1:3]); b=defs(sys.argv[3:5])
skip=re.compile(r'^(SDSORT|DEFAULT_(K|bed|BED)|STRING_|CUSTOM_VERSION|_|HAS_|PROUI|.*_INCLUDED$)')
print("## only in KT-Oct (standard) config:");[print(' ',k,sorted(a[k])) for k in sorted(set(a)-set(b)) if not skip.match(k)]
print("## only in current MriscocProUI config:");[print(' ',k,sorted(b[k])) for k in sorted(set(b)-set(a)) if not skip.match(k)]
print("## different values:");[print(' ',k,sorted(a[k]),'->',sorted(b[k])) for k in sorted(set(a)&set(b)) if a[k]!=b[k] and not skip.match(k)]
