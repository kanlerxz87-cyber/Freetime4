import os,urllib.request,ssl,urllib.error,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p12",exist_ok=True)
URLS=[("espn_cal","https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/cal/schedule?season=2026"),
 ("espn_stan","https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/stanford/schedule?season=2026"),
 ("espn_cal27","https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/cal/schedule?season=2027"),
 ("espn_stan27","https://site.api.espn.com/apis/site/v2/sports/football/college-football/teams/stanford/schedule?season=2027"),
 ("espn_nfl27_sb","https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2027&seasontype=1&limit=1000"),
 ("espn_nfl27_p","https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?dates=2027&seasontype=3&limit=1000")]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p12/{n}.json","wb").write(b); rep.append(f"| {n} | 200 | {len(b)} | {u} |"); print("OK",n,len(b))
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {u} | {type(e).__name__} |"); print("ERR",n,type(e).__name__)
open("data/p12-report.md","w").write("| name | status | bytes | url |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
