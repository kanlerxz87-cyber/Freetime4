import os,urllib.request,ssl,urllib.error,re,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p4",exist_ok=True)
urls=[("byweek_1","https://www.nfl.com/schedules/2026/by-week/week-1/"),
      ("byweek_5","https://www.nfl.com/schedules/2026/by-week/week-5/"),
      ("byweek_18","https://www.nfl.com/schedules/2026/by-week/week-18/"),
      ("byweek_2027_1","https://www.nfl.com/schedules/2027/by-week/week-1/"),
      ("sf_sched","https://www.49ers.com/schedule/"),
      ("sf_sched_2026","https://www.49ers.com/schedule/2026/"),
      ("wwo_past_all","https://www.westwoodonesports.com/more/eventGrid?id=all&range=past&offset=0&limit=400&timezone=America/Los_Angeles"),
      ("wwo_all_2026","https://www.westwoodonesports.com/more/eventGrid?id=all&range=current&offset=0&limit=400&timezone=America/Los_Angeles&year=2026")]
rep=[]
for n,u in urls:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p4/{n}.html","wb").write(b)
        cards=len(re.findall(r'absolute inset-0" data-analytics',b.decode('utf-8','ignore')))
        rep.append(f"| {n} | {f.status} | {len(b)} | cards={cards} | {u} |"); print("OK",f.status,len(b),n,"cards",cards)
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | - | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | - | {u} | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
open("data/p4-report.md","w").write("| name | status | bytes | note | url |\n|---|---|---|---|---|\n"+"\n".join(rep)+"\n")
