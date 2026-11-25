import os,urllib.request,ssl,urllib.error,re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p11",exist_ok=True)
URLS=[
 ("knbr_stanford","https://www.knbr.com/stanford-football/"),
 ("knbr_stanford2","https://www.knbr.com/stanford/"),
 ("knbr_program","https://www.knbr.com/knbr-1050-program-schedule/"),
 ("knbr_program2","https://www.knbr.com/program-schedule/"),
 ("knbr_giants2","https://www.knbr.com/san-francisco-giants/"),
 ("sf_radio_team","https://www.49ers.com/team/radio/"),
 ("sf_radio_network2","https://www.49ers.com/team/radio-network-affiliates/"),
 ("cal_radio2","https://calbears.com/sports/football/coaches"),
 ("ksfo_site","https://www.ksfo.com/"),
 ("wwo_station_finder","https://www.westwoodonesports.com/stations/?zip=94122"),
 ("mlb_giants_radio_net","https://www.mlb.com/giants/team/broadcasters#radio-network"),
 ("stan_football_radio","https://gostanford.com/sports/football/schedule?season=2026&view=list"),
]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p11/{n}","wb").write(b)
        rep.append(f"| {n} | 200 | {len(b)} | {u} |"); print("OK",n,len(b))
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {u} | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
open("data/p11-report.md","w").write("| name | status | bytes | url |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
