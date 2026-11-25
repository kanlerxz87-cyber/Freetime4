"""Minimal parser for Nuxt 3 __NUXT_DATA__ (devalue) payloads."""
import json, re, sys

SPECIAL = {-1: None, -2: float('nan'), -3: float('inf'), -4: -0.0, -5: float('-inf')}

class Devalue:
    def __init__(self, payload):
        self.p = payload
        self.memo = {}
    def resolve(self, i):
        if isinstance(i, bool) or i is None:
            return i
        if isinstance(i, str) or isinstance(i, float):
            return i
        if not isinstance(i, int):
            return i
        if i in self.memo:
            return self.memo[i]
        if i < 0:
            return SPECIAL.get(i, None)
        v = self.p[i]
        if isinstance(v, (str, bool, float)) or v is None:
            out = v
        elif isinstance(v, int):
            out = self.resolve(v)
        elif isinstance(v, list):
            out = self._list(v)
        elif isinstance(v, dict):
            out = {}
            self.memo[i] = out
            for k, val in v.items():
                out[k] = self.resolve(val)
            return out
        else:
            out = v
        self.memo[i] = out
        return out
    def _list(self, v):
        if v and isinstance(v[0], str) and v[0] in ('Reactive','ShallowReactive','Ref','ShallowRef','Object','Set','Map','Date','BigInt','RegExp','URL','null','Symbol','Array'):
            tag = v[0]
            if tag in ('Reactive','ShallowReactive','Ref','ShallowRef','Object'):
                return self.resolve(v[1])
            if tag in ('null',):
                return None
            if tag == 'Set':
                return [self.resolve(x) for x in v[1:]]
            if tag == 'Map':
                return {self.resolve(v[k]): self.resolve(v[k+1]) for k in range(1, len(v)-1, 2)}
            if tag == 'Date':
                return v[1]
            return v[1:]
        return [self.resolve(x) for x in v]

def extract(html, tag='application/json'):
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, flags=re.S)
    if not m:
        return None
    payload = json.loads(m.group(1))
    d = Devalue(payload)
    return d.resolve(0)

if __name__ == '__main__':
    html = open(sys.argv[1], encoding='utf-8', errors='ignore').read()
    data = extract(html)
    print(json.dumps(data, indent=1)[:3000])
