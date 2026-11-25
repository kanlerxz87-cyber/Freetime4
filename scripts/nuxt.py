import json,re
def parse(path):
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
def dumps(o,**kw):
    seen=set()
    def d(x,depth=0):
        if depth>12: return '...'
        if isinstance(x,dict): return {k:d(v,depth+1) for k,v in list(x.items())[:40]}
        if isinstance(x,list): return [d(v,depth+1) for v in x[:40]]
        return x
    return json.dumps(d(o),**kw)
