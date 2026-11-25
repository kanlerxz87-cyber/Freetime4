"""Extract schedule events from a Nuxt/oas athletics site payload."""
import json,re,sys

def load(path):
    s=open(path,encoding='utf-8',errors='ignore').read()
    m=re.search(r'id="__NUXT_DATA__"[^>]*>(.*?)</script>',s,flags=re.S)
    p=json.loads(m.group(1)); memo={}
    def resolve(i):
        if isinstance(i,bool) or i is None or isinstance(i,float) or isinstance(i,str): return i
        if not isinstance(i,int): return i
        if i<0: return None
        if i>=len(p): return i
        if i in memo: return memo[i]
        v=p[i]
        if isinstance(v,(str,bool,float)) or v is None: return v
        if isinstance(v,int): return resolve(v)
        if isinstance(v,list):
            if v and isinstance(v[0],str) and v[0] in ('Reactive','ShallowReactive','Ref','ShallowRef','Object'): return resolve(v[1])
            out=[];memo[i]=out
            for x in v: out.append(resolve(x))
            return out
        if isinstance(v,dict):
            out={};memo[i]=out
            for k,x in v.items(): out[k]=resolve(x)
            return out
        return v
    return resolve(0)

def find_event_dicts(obj,out=None,depth=0,seen=None):
    if out is None: out=[]
    if seen is None: seen=set()
    if depth>14 or id(obj) in seen: return out
    seen.add(id(obj))
    if isinstance(obj,dict):
        ks=set(obj.keys())
        if {'start_date_utc','start_date'} <= ks and ('status' in ks or 'time' in ks):
            out.append(obj)
        for v in obj.values(): find_event_dicts(v,out,depth+1,seen)
    elif isinstance(obj,list):
        for v in obj: find_event_dicts(v,out,depth+1,seen)
    return out

if __name__=='__main__':
    r=load(sys.argv[1])
    evs=find_event_dicts(r)
    print('events found:',len(evs))
    for e in evs[:3]:
        print(json.dumps({k:e[k] for k in list(e.keys())},indent=1,default=str)[:2500])
