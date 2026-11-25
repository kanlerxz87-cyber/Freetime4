import os,urllib.request,ssl,urllib.error,re,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p7",exist_ok=True)
URLS=[
 ("stan_print","https://gostanford.com/sports/football/schedule/print"),
 ("stan_list","https://gostanford.com/sports/football/schedule/list"),
 ("stan_seasonid","https://gostanford.com/sports/football/schedule?season_id=2650"),
 ("stan_2627","https://gostanford.com/sports/football/schedule/2026-27"),
 ("stan_apiv2","https://gostanford.com/api/v2/sports/football/schedule?season=2026&schedule_id=2650"),
 ("stan_table","https://gostanford.com/sports/football/schedule?view=table"),
 ("stan_schedtxt","https://gostanford.com/sports/football/schedule/2026-27/"),
 ("cal_pdf","https://calbears.com/sports/football/schedule/pdf"),
 ("sf_rsc","https://www.49ers.com/schedule/2026/"),
]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p7/{n}","wb").write(b)
        t=b.decode('utf-8','ignore')
        dates=len(re.findall(r'20\d\d-\d\d-\d\dT\d\d:\d\d',t))
        rep.append(f"| {n} | 200 | {len(b)} | datetimes={dates} | {u} |"); print("OK",n,len(b),"dt",dates)
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | - | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {type(e).__name__} | {u} |"); print("ERR",n,type(e).__name__)
open("data/p7-report.md","w").write("| name | status | bytes | note | url |\n|---|---|---|---|---|\n"+"\n".join(rep)+"\n")
