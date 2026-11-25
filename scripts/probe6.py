import os,urllib.request,ssl,urllib.error,re,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p6",exist_ok=True)
def get(u,h=None,timeout=40):
    hh={"User-Agent":UA}; 
    if h: hh.update(h)
    r=urllib.request.Request(u,headers=hh)
    with urllib.request.urlopen(r,timeout=timeout,context=ssl.create_default_context()) as f: return f.status,f.read()
rep=[]
def save(n,u,h=None):
    try:
        st,b=get(u,h); open(f"data/_p6/{n}","wb").write(b)
        rep.append(f"| {n} | {st} | {len(b)} | {u} |"); print("OK",n,st,len(b)); return b
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {u} | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
    return None
b=save("stan_bundle.js","https://gostanford.com/_nuxt/C3S7Mjr8.js")
cands=[]
if b:
    t=b.decode('utf-8','ignore')
    for u in sorted(set(re.findall(r'https?://[a-zA-Z0-9._/:%-]{10,110}',t))):
        if any(k in u for k in ('api','oas','sidearm','sports','.edu','.com')) and 'google' not in u and 'gstatic' not in u and 'w3.org' not in u:
            cands.append(u)
    print("candidates:",cands[:25])
    # look for api path patterns
    print("paths:", sorted(set(re.findall(r'["\'`](/api/[a-zA-Z0-9/_.{}$:-]{2,70})',t)))[:25])
for u in cands[:12]:
    n="cand_"+re.sub(r'[^a-z0-9]+','_',u)[:50]
    save(n,u)
open("data/p6-report.md","w").write("| name | status | bytes | url |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
