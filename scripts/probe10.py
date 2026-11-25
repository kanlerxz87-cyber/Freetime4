import os,urllib.request,ssl,urllib.error,re,json
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p10",exist_ok=True)
URLS=[
 ("stan_radio_info","https://gostanford.com/news/2013/4/17/radio-information"),
 ("knbr_49ers_news","https://www.knbr.com/49ers/"),
 ("sf_radio_2026","https://www.49ers.com/team/Radio-Network"),
 ("sf_sched_2027_season","https://www.49ers.com/schedule/2027/"),
 ("nfl_probowl2","https://www.nfl.com/pro-bowl-games/"),
 ("nfl_post_index","https://www.nfl.com/schedules/post/"),
 ("nfl_post_2026w","https://www.nfl.com/schedules/2026/by-week/week-19/"),
 ("nfl_post_2026w2","https://www.nfl.com/schedules/2026/by-week/week-20/"),
 ("nfl_post_2026w3","https://www.nfl.com/schedules/2026/by-week/week-21/"),
 ("wwo_event2","https://www.westwoodonesports.com/events/548511/"),
 ("wwo_nfl2025","https://www.westwoodonesports.com/more/eventGrid?id=all&range=past&offset=0&limit=400&timezone=America/Los_Angeles&year=2025"),
 ("mlb_schedule_page_2027","https://www.mlb.com/schedule/2027-06-15"),
]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p10/{n}","wb").write(b)
        cards=len(re.findall(r'absolute inset-0" data-analytics',b.decode('utf-8','ignore')))
        rep.append(f"| {n} | 200 | {len(b)} | cards={cards} | {u} |"); print("OK",n,len(b),"cards",cards)
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | - | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {type(e).__name__} | {u} |"); print("ERR",n,type(e).__name__)
open("data/p10-report.md","w").write("| name | status | bytes | note | url |\n|---|---|---|---|---|\n"+"\n".join(rep)+"\n")
