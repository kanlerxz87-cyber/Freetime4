import os,urllib.request,ssl,urllib.error
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p3",exist_ok=True)
urls=[
 ("nflapi_sched","https://api.nfl.com/api/v1/schedules?season=2026&seasonType=REG"),
 ("nflapi_sched2","https://api.nfl.com/schedules/2026/REG"),
 ("nflcomm","https://nflcommunications.com/Pages/Schedule.aspx"),
 ("nflcomm_pdf","https://nflcommunications.com/Documents/2026%20Schedule.pdf"),
 ("nfl49ers","https://www.49ers.com/schedule/"),
 ("nfl49ers2027","https://www.49ers.com/schedule/2027/"),
 ("espn_sf27","https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/sf/schedule?season=2027"),
 ("stan_sched2026","https://gostanford.com/sports/football/schedule/2026"),
 ("stan_q27","https://gostanford.com/sports/football/schedule?season=2027"),
 ("stan_api1","https://gostanford.com/api/v2/sports/football/2026/schedule"),
 ("stan_ical","https://gostanford.com/ical/football.ics"),
 ("stan_ics","https://gostanford.com/sports/football/schedule.ics"),
 ("cal_season2627","https://calbears.com/sports/football/schedule/season/2026-27"),
 ("cal_2027","https://calbears.com/sports/football/schedule/2027"),
 ("cal_api1","https://calbears.com/api/v2/sports/football/2026/schedule"),
 ("stan_oas1","https://gostanford.com/api/oas/v1/schedule?sport=football&season=2026"),
 ("stan_oas2","https://gostanford.com/api/oas/schedules/football"),
 ("wwo_more","https://www.westwoodonesports.com/more/eventGrid?id=all&range=past&offset=0&limit=400&timezone=America/Los_Angeles"),
 ("knbr_giants","https://www.knbr.com/giants/"),
 ("knbr_49ers","https://www.knbr.com/49ers/"),
 ("knbr_athletics","https://www.knbr.com/athletics/"),
 ("knbr_shows","https://www.knbr.com/shows/"),
 ("mlb_gd2_2027","https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&startDate=2027-10-01&endDate=2027-11-05"),
 ("mlb_post27","https://statsapi.mlb.com/api/v1/schedule/postseason?sportId=1&season=2027"),
]
rep=[]
for name,u in urls:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f:
            b=f.read()
        open(f"data/_p3/{name}","wb").write(b)
        rep.append(f"| {name} | {f.status} | {len(b)} | {u} |")
        print("OK",f.status,len(b),name)
    except urllib.error.HTTPError as e:
        rep.append(f"| {name} | {e.code} | 0 | {u} |"); print("HTTP",e.code,name)
    except Exception as e:
        rep.append(f"| {name} | ERR | 0 | {u} | {type(e).__name__}"); print("ERR",name,type(e).__name__)
open("data/p3-report.md","w").write("| name | status | bytes | url |\n|---|---|---|---|\n"+"\n".join(rep)+"\n")
