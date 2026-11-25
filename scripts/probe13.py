import os,re,json,time,urllib.request,ssl,urllib.error
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
OUT="data/raw/wwo_events"; os.makedirs(OUT,exist_ok=True)
lst=json.load(open("data/wwo_events_list.json"))
print("events to fetch:",len(lst))
ok=miss=err=0
for i,e in enumerate(lst):
    href=e["href"]; fn=os.path.join(OUT, href.strip("/").replace("/","_")+".json")
    if os.path.exists(fn): ok+=1; continue
    url="https://www.westwoodonesports.com"+href
    try:
        r=urllib.request.Request(url,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=30,context=ssl.create_default_context()) as f: b=f.read().decode("utf-8","ignore")
        m=re.search(r'<script type="application/ld\+json">\s*(\{.*?"@type"\s*:\s*"Event".*?\})\s*</script>',b,flags=re.S)
        if not m: miss+=1; continue
        d=json.loads(m.group(1))
        json.dump({"href":href,"url":url,"ld":d},open(fn,"w"))
        ok+=1
    except Exception as ex:
        err+=1
print("ok",ok,"missing",miss,"err",err)
