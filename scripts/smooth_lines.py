import json, math, glob, os
SRC='data/geojson'; OUT='data/geojson_smooth'
os.makedirs(OUT, exist_ok=True)
def proj(p, lat0):
    k=math.cos(math.radians(lat0))
    return (p[0]*111.32*k, p[1]*110.57)
def dp(pts, tol, P):
    if len(pts)<3: return pts
    a,b=P[0],P[-1]; dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy)
    best,bi=0,0
    for i in range(1,len(pts)-1):
        x,y=P[i]
        d=abs(dy*(x-a[0])-dx*(y-a[1]))/L if L else math.hypot(x-a[0],y-a[1])
        if d>best: best,bi=d,i
    if best<=tol: return [pts[0],pts[-1]]
    return dp(pts[:bi+1],tol,P[:bi+1])[:-1]+dp(pts[bi:],tol,P[bi:])
def chaikin(pts, n=3):
    for _ in range(n):
        if len(pts)<3: return pts
        out=[pts[0]]
        for a,b in zip(pts,pts[1:]):
            out.append([0.75*a[0]+0.25*b[0],0.75*a[1]+0.25*b[1]])
            out.append([0.25*a[0]+0.75*b[0],0.25*a[1]+0.75*b[1]])
        out.append(pts[-1]); pts=out
    return pts
def close(a,b,lat0,tol=1.0):
    A,B=proj(a,lat0),proj(b,lat0); return math.hypot(A[0]-B[0],A[1]-B[1])<tol
def merge(parts, lat0):
    parts=[list(p) for p in parts if len(p)>1]; chains=[]
    while parts:
        c=parts.pop(0); grown=True
        while grown:
            grown=False
            for i,p in enumerate(parts):
                if close(c[-1],p[0],lat0): c+=p[1:]
                elif close(c[-1],p[-1],lat0): c+=p[::-1][1:]
                elif close(c[0],p[-1],lat0): c=p[:-1]+c
                elif close(c[0],p[0],lat0): c=p[::-1][:-1]+c
                else: continue
                parts.pop(i); grown=True; break
        chains.append(c)
    return chains
for f in sorted(glob.glob(SRC+'/*.geojson')):
    name=os.path.basename(f)
    if name=='terminals.geojson': continue
    g=json.load(open(f)); feats=[]
    for ft in g['features']:
        if not ft.get('geometry'): continue
        ge=ft['geometry']; parts=ge['coordinates'] if ge['type']=='MultiLineString' else [ge['coordinates']]
        feats.append((ft['properties'],parts))
    groups={}
    for props,parts in feats: groups.setdefault(props.get('Name'),[props,[]])[1].extend(parts)
    outf=[]; vin=vout=0
    for nm,(props,parts) in groups.items():
        lat0=sum(p[1] for q in parts for p in q)/sum(len(q) for q in parts)
        lines=[]
        for c in merge(parts,lat0):
            vin+=len(c)
            s=dp(c,0.7,[proj(p,lat0) for p in c])
            s=chaikin(s,3)
            s=[[round(x,5),round(y,5)] for x,y in s]
            vout+=len(s); lines.append(s)
        outf.append({"type":"Feature","properties":{"Name":nm},"geometry":{"type":"MultiLineString","coordinates":lines}})
    json.dump({"type":"FeatureCollection","features":outf},open(os.path.join(OUT,name),'w'),separators=(',',':'))
    print(name,'features',len(g['features']),'->',len(outf),'chains',sum(len(x['geometry']['coordinates']) for x in outf),'verts',vin,'->',vout,os.path.getsize(os.path.join(OUT,name)))
