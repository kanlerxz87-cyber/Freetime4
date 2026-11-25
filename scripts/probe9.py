import os,urllib.request,ssl,urllib.error,re
UA="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
os.makedirs("data/_p9",exist_ok=True)
URLS=[
 ("nfl_pre_a","https://www.nfl.com/schedules/2026/preseason/"),
 ("nfl_pre_b","https://www.nfl.com/schedules/preseason/"),
 ("nfl_pre_c","https://www.nfl.com/schedules/2026/PRE1/"),
 ("nfl_pre_d","https://www.nfl.com/schedules/2026/pre/1/"),
 ("nfl_post_b","https://www.nfl.com/schedules/2026/postseason/"),
 ("nfl_post_c","https://www.nfl.com/schedules/postseason/"),
 ("nfl_post_d","https://www.nfl.com/schedules/2026/playoffs/"),
 ("nfl_probowl","https://www.nfl.com/pro-bowl/"),
 ("sf_2026_print","https://www.49ers.com/schedule/printable/"),
 ("sf_radio","https://www.49ers.com/team/radio-network"),
 ("stan_fb_page","https://gostanford.com/sports/football"),
 ("cal_fb_page","https://calbears.com/sports/football"),
 ("stan_radio2","https://gostanford.com/sports/football/links"),
 ("knbr_about","https://www.knbr.com/about/"),
 ("knbr_contact","https://www.knbr.com/contact/"),
 ("giants_aff","https://www.mlb.com/giants/fans/radio"),
 ("athl_aff","https://www.mlb.com/athletics/fans/radio"),
 ("wwo_aff_1","https://www.westwoodonesports.com/stations/?state=CA"),
 ("mlb_giants_26","https://www.mlb.com/giants/schedule/2026-04"),
]
rep=[]
for n,u in URLS:
    try:
        r=urllib.request.Request(u,headers={"User-Agent":UA})
        with urllib.request.urlopen(r,timeout=40,context=ssl.create_default_context()) as f: b=f.read()
        open(f"data/_p9/{n}","wb").write(b)
        cards=len(re.findall(r'absolute inset-0" data-analytics',b.decode('utf-8','ignore')))
        rep.append(f"| {n} | 200 | {len(b)} | cards={cards} | {u} |"); print("OK",n,len(b),"cards",cards)
    except urllib.error.HTTPError as e: rep.append(f"| {n} | {e.code} | 0 | - | {u} |"); print("HTTP",e.code,n)
    except Exception as e: rep.append(f"| {n} | ERR | 0 | {type(e).__name__} | {u} |"); print("ERR",n,type(e).__name__)
open("data/p9-report.md","w").write("| name | status | bytes | note | url |\n|---|---|---|---|---|\n"+"\n".join(rep)+"\n")
