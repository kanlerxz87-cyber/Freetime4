import os,urllib.request,ssl,urllib.error,re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p5",exist_ok=True)
targets=[]
for yr in (2026,):
    for st,weeks in (("PRE",range(0,5)),("REG",range(1,19)),("POST",range(19,24))):
        for w in weeks:
            targets.append((f"{yr}_{st}_{w}", f"https://www.nfl.com/schedules/{yr}/by-week/week-{w}/"))
# alternative POST urls
targets += [("post_alt","https://www.nfl.com/schedules/2026/post-season/"),
            ("wwo_past","https://www.westwoodonesports.com/more/eventGrid?id=all&range=past&offset=0&limit=400&timezone=America/Los_Angeles"),
            ("mlb_alls","https://statsapi.mlb.com/api/v1/schedule?sportId=1&season=2026&gameTypes=A,E,C")]
rep=[]
for n,u in targets:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p5/{n}.html","wb").write(b)
        c=len(re.findall(r'absolute inset-0" data-analytics',b.decode('utf-8','ignore')))
        rep.append(f"| {n} | 200 | {len(b)} | cards={c} |"); print("OK",n,len(b),"cards",c)
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | - |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
open("data/p5-report.md","w").write("| name | status | bytes | note |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
