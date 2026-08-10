#!/usr/bin/env python3
"""Suomen järvet — integrated build: SYKE level(+history) & ice, DENSE Järviwiki
temperature (ask API, +sparkline +citizen/authority badge), OSM nearest-town,
59k register lakes (reused), Voyager basemap, FI/EN, 4 lenses, search."""
import json, urllib.request, urllib.parse, math, os, re, datetime
HY='https://rajapinnat.ymparisto.fi/api/Hydrologiarajapinta/1.1/odata'
LK='https://rajapinnat.ymparisto.fi/api/jarvirajapinta/1.0/odata'
JW='https://www.jarviwiki.fi/w/api.php'
BASE=os.path.dirname(os.path.abspath(__file__))
CD=os.path.join(BASE,'dist'); os.makedirs(CD,exist_ok=True)
TMPL=os.path.join(BASE,'template.html')
TODAY=datetime.date.today()

def GET(url,timeout=120):
    return json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'Mozilla/5.0'}),timeout=timeout))
def odata(url, cap=400000, tag=''):
    rows=[]; root=url.split('/odata/')[0]+'/odata/'; pages=0
    while url and len(rows)<cap and pages<900:
        pages+=1; d=GET(url)
        rows.extend(d.get('value',[]))
        if tag and pages%40==0: print(f"   {tag}: {len(rows)}...",flush=True)
        nxt=d.get('odata.nextLink'); url = nxt if (nxt or '').startswith('http') else (root+nxt if nxt else None)
    return rows
def dms(s):
    if not s: return None
    s=s.strip()
    if '.' in s:
        try: return float(s)
        except: return None
    if len(s)<5: return None
    try: return int(s[:2])+int(s[2:4])/60+int(s[4:6])/3600
    except: return None
def clean(n):
    n=(n or '').strip(); n=re.sub(r'\s*\(N\d.*$','',n); return re.sub(r'\s*[×x]\d+$','',n).strip()
def md(iso): return iso[5:].replace('-','.')  # 2026-05-01 -> 05.01

# ---------- towns (OSM Overpass, fallback) ----------
FALLBACK=[["Helsinki",24.94,60.17],["Espoo",24.65,60.21],["Tampere",23.76,61.50],["Vantaa",25.04,60.29],["Oulu",25.47,65.01],["Turku",22.27,60.45],["Jyväskylä",25.75,62.24],["Kuopio",27.68,62.89],["Lahti",25.66,60.98],["Pori",21.80,61.49],["Joensuu",29.76,62.60],["Lappeenranta",28.19,61.06],["Vaasa",21.62,63.10],["Seinäjoki",22.84,62.79],["Rovaniemi",25.73,66.50],["Mikkeli",27.27,61.69],["Kotka",26.94,60.47],["Kokkola",23.13,63.84],["Kajaani",27.73,64.22],["Savonlinna",28.88,61.87],["Kemi",24.56,65.74],["Iisalmi",27.19,63.56],["Sodankylä",26.59,67.42],["Kuusamo",29.19,65.96],["Tornio",24.14,65.85],["Varkaus",27.87,62.31],["Nurmes",29.14,63.54],["Inari",27.03,68.90],["Kittilä",24.91,67.65],["Hämeenlinna",24.46,60.99],["Porvoo",25.66,60.39],["Raahe",24.48,64.68]]
def towns():
    q='[out:json][timeout:80];area["ISO3166-1"="FI"][admin_level=2]->.fi;(node["place"~"^(city|town)$"](area.fi););out qt;'
    try:
        req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=('data='+urllib.parse.quote(q)).encode(),headers={'User-Agent':'suomen-jarvet/1.0 (github.com/nanwer)','Content-Type':'application/x-www-form-urlencoded','Accept':'application/json'})
        d=json.load(urllib.request.urlopen(req,timeout=100)); ts=[]
        for e in d.get('elements',[]):
            nm=e.get('tags',{}).get('name:fi') or e.get('tags',{}).get('name')
            if nm and 'lat' in e and 'lon' in e: ts.append([nm,round(e['lon'],4),round(e['lat'],4)])
        return ts if len(ts)>50 else FALLBACK
    except Exception as ex:
        print("   overpass fail -> fallback:",ex); return FALLBACK
print("towns ...",flush=True); TOWNS=towns(); print("   towns:",len(TOWNS))

print("stations ...",flush=True)
st={s['Paikka_Id']:s for s in odata(f"{HY}/Paikka?%24select=Paikka_Id,Nimi,JarviNimi,KuntaNimi,KoordLat,KoordLong&%24top=6000")}
def coord(pid):
    s=st.get(pid)
    if not s: return None
    la=dms(s.get('KoordLat')); lo=dms(s.get('KoordLong'))
    return (lo,la,clean(s.get('JarviNimi') or s.get('Nimi')),(s.get('KuntaNimi') or '').strip()) if la and lo else None

print("water level history (since 2026-05-01) ...",flush=True)
byst={}
for r in odata(f"{HY}/Vedenkorkeus?%24filter=Aika%20ge%20datetime'{(TODAY-datetime.timedelta(days=90)).isoformat()}T00:00:00'&%24top=200000",tag='WL'):
    try: byst.setdefault(r['Paikka_Id'],[]).append((r['Aika'][:10],float(r['Arvo'])))
    except: pass
def d14(pts):
    last=pts[-1]; tgt=datetime.date.fromisoformat(last[0])-datetime.timedelta(days=14)
    ref=min(pts,key=lambda p:abs((datetime.date.fromisoformat(p[0])-tgt).days)); return round(last[1]-ref[1],1)
levelF=[]
for pid,pts in byst.items():
    c=coord(pid)
    if not c: continue
    pts.sort(); ser=[round(v) for _,v in pts]
    if len(ser)>150: ser=ser[::len(ser)//150+1]
    levelF.append({"type":"Feature","geometry":{"type":"Point","coordinates":[round(c[0],5),round(c[1],5)]},
      "properties":{"name":c[2],"kunta":c[3],"d":d14(pts) if len(pts)>=2 else None,"h":ser,"h0":md(pts[0][0]),"h1":md(pts[-1][0])}})
ld=sorted(abs(f["properties"]["d"]) for f in levelF if f["properties"]["d"] is not None)
p90=round(max(2.0,ld[int(len(ld)*0.9)]),1) if ld else 10
ldate=max(f["properties"]["h1"] for f in levelF)

print("DENSE temperature via Järviwiki ask API ...",flush=True)
def jw_temp(series_days=30):
    since=(TODAY-datetime.timedelta(days=series_days)).isoformat()
    q=("[[ObsCode::temp]][[Pintaveden lämpötila::>0]][[Päivämäärä::>"+since+"]]"
       "|?Koordinaatit|?Päivämäärä|?Pintaveden lämpötila|?SiteName|?Ylläpito|sort=Päivämäärä|order=descending|limit=20000")
    d=GET(JW+"?action=ask&format=json&query="+urllib.parse.quote(q))
    obs=[]
    for k,v in d['query']['results'].items():
        po=v.get('printouts',{}); ko=po.get('Koordinaatit') or []; tp=po.get('Pintaveden lämpötila') or []; dt=po.get('Päivämäärä') or []
        if not(ko and tp and dt): continue
        try: lat=float(ko[0]['lat']); lon=float(ko[0]['lon']); tv=float(tp[0]['value'] if isinstance(tp[0],dict) else tp[0]); ts=int(dt[0]['timestamp'])
        except: continue
        sn=po.get('SiteName') or []; site=(sn[0].get('fulltext') if sn and isinstance(sn[0],dict) else (sn[0] if sn else '')) or ''
        yl=po.get('Ylläpito') or []; maint=(yl[0].get('fulltext') if yl and isinstance(yl[0],dict) else (yl[0] if yl else ''))
        obs.append((site,lat,lon,tv,ts,maint))
    return obs
raw=jw_temp(30)
bysite={}
for site,lat,lon,tv,ts,maint in raw: bysite.setdefault(site,[]).append((ts,tv,lat,lon,maint))
tempF=[]; fresh=(TODAY-datetime.timedelta(days=7))
for site,arr in bysite.items():
    arr.sort()
    ts,tv,lat,lon,maint=arr[-1]
    ddate=datetime.datetime.utcfromtimestamp(ts).date()
    if ddate<fresh: continue                      # 7-day freshness window
    name=re.sub(r'\s*\(.*$','',site).strip() or site
    ser=[t for _,t,_,_,_ in arr][-30:]
    m='a' if 'iranomais' in maint else 'c'
    tempF.append({"type":"Feature","geometry":{"type":"Point","coordinates":[round(lon,5),round(lat,5)]},
      "properties":{"name":name,"kunta":"","t":round(tv,1),"date":ddate.strftime('%-d.%-m.'),"m":m,
        "h":[round(x,1) for x in ser],"h0":arr[0][0] and datetime.datetime.utcfromtimestamp(arr[0][0]).date().strftime('%-d.%-m.'),"h1":ddate.strftime('%-d.%-m.')}})
tvals=[f["properties"]["t"] for f in tempF]; tmin=round(min(tvals)); tmax=round(max(tvals))
ncit=sum(1 for f in tempF if f["properties"]["m"]=='c')
print(f"   temp sites (7d fresh): {len(tempF)}  citizen/expert: {ncit}  range {tmin}-{tmax}C")

print("ice-out spring 2026 ...",flush=True)
icebyst={}
for r in odata(f"{HY}/JaatJaanlahto?%24filter=Arvo%20ge%20datetime'{TODAY.year}-03-01T00:00:00'%20and%20Arvo%20le%20datetime'{TODAY.year}-06-30T00:00:00'&%24top=2000"):
    dd=r['Arvo'][:10]; icebyst[r['Paikka_Id']]=max(icebyst.get(r['Paikka_Id'],dd),dd)
iceF=[]
for pid,dd in icebyst.items():
    c=coord(pid)
    if not c: continue
    iceF.append({"type":"Feature","geometry":{"type":"Point","coordinates":[round(c[0],5),round(c[1],5)]},"properties":{"name":c[2],"kunta":c[3],"date":dd,"doy":datetime.date.fromisoformat(dd).timetuple().tm_yday}})
idoys=[f["properties"]["doy"] for f in iceF]; imin=min(idoys); imax=max(idoys)
def dlabel(doy): d=datetime.date(TODAY.year,1,1)+datetime.timedelta(days=doy-1); return f"{d.day}.{d.month}."
print(f"   ice-out: {len(iceF)} ({dlabel(imin)}–{dlabel(imax)})")

# ---------- lakes (reuse cached 59k register) ----------
LGJ=os.path.join(BASE,'lakes.geojson'); lp=os.path.join(CD,'lakes.geojson')
if os.path.exists(LGJ) and os.path.getsize(LGJ)>8e6:
    data=open(LGJ,encoding='utf-8').read(); nlake=len(json.loads(data)['features']); print("reusing committed lakes.geojson:",nlake)
else:
    print("ALL register lakes (~59k) ...",flush=True); feats=[]
    for L in odata(f"{LK}/Jarvi?%24select=Nimi,KuntaNimi,VesalNimi,KoordErLat,KoordErLong,Vesiala,SyvyysSuurin,SyvyysKeski,Tilavuus,Rantaviiva&%24top=70000",tag='lakes'):
        try: la=float(L['KoordErLat']); lo=float(L['KoordErLong'])
        except: continue
        if not(59<la<71 and 19<lo<32): continue
        p={"n":clean(L.get('Nimi')),"k":(L.get('KuntaNimi') or '').strip()}
        try: ar=float(L['Vesiala']); p["a"]=round(ar/100,2); p["r"]=round(max(1.4,min(9.0,1.4+1.05*(math.log10(ar)-2))),2)
        except: p["r"]=1.4
        for s2,dd in [('SyvyysSuurin','dmax'),('SyvyysKeski','dmean'),('Rantaviiva','sh')]:
            try: p[dd]=round(float(L[s2]),1)
            except: pass
        try:
            vol=float(L['Tilavuus'])/1000.0
            if vol>0: p["vol"]=round(vol,1)
        except: pass
        ws=(L.get('VesalNimi') or '').strip()
        if ws: p["ws"]=ws
        feats.append({"type":"Feature","geometry":{"type":"Point","coordinates":[round(lo,5),round(la,5)]},"properties":p})
    data=json.dumps({"type":"FeatureCollection","features":feats},ensure_ascii=False); open(LGJ,"w",encoding='utf-8').write(data); nlake=len(feats)
    print("   mapped lakes:",nlake)
open(lp,"w",encoding='utf-8').write(data)  # copy static register into dist/ for serving

CFG={"level":{"type":"FeatureCollection","features":levelF},"temp":{"type":"FeatureCollection","features":tempF},
 "ice":{"type":"FeatureCollection","features":iceF},"towns":TOWNS,"p90":p90,"ldate":ldate,"tmin":tmin,"tmax":tmax,
 "imin":imin,"imax":imax,"iloD":dlabel(imin),"ihiD":dlabel(imax),"nlevel":len(levelF),"ntemp":len(tempF),"nice":len(iceF),"nlake":nlake}
open(os.path.join(CD,"index.html"),"w").write(open(TMPL).read().replace('__CFG__',json.dumps(CFG,ensure_ascii=False)))
print("SUMMARY:",{k:CFG[k] for k in ['nlevel','ntemp','nice','nlake','p90']}," index.html",round(os.path.getsize(os.path.join(CD,'index.html'))/1e6,2),"MB")
