import os,urllib.request,ssl,urllib.error,re,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p8",exist_ok=True)
URLS=[("wwo_ev_upcoming","https://www.westwoodonesports.com/events/548511"),
 ("wwo_ev_past","https://www.westwoodonesports.com/events/"),
 ("wwo_events_list","https://www.westwoodonesports.com/events/"),
 ("giants_radio","https://www.mlb.com/giants/team/broadcasters"),
 ("giants_affiliates","https://www.mlb.com/giants/fans/radio-network"),
 ("mlb_giants_schedule","https://www.mlb.com/giants/schedule"),
 ("sf49ers_radio","https://www.49ers.com/team/radio-network/"),
 ("athletics_radio","https://www.mlb.com/athletics/team/broadcasters"),
 ("stan_radio","https://gostanford.com/sports/football/radio"),
 ("cal_radio","https://calbears.com/sports/football/radio"),
 ("knbr_stations","https://www.knbr.com/stations/"),
 ("wwo_stations","https://www.westwoodonesports.com/stations/"),
 ("espn_nfl_2027","https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2027&limit=1000"),
]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p8/{n}","wb").write(b)
        rep.append(f"| {n} | 200 | {len(b)} | {u} |"); print("OK",n,len(b))
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {u} | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
open("data/p8-report.md","w").write("| name | status | bytes | url |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
