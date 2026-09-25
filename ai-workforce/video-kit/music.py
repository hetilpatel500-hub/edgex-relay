import numpy as np, wave, sys
dur=float(sys.argv[1]); outp=sys.argv[2]; seed=int(sys.argv[3]) if len(sys.argv)>3 else 0
sr=44100; n=int(sr*(dur+1.5)); t=np.arange(n)/sr
bpm=100; beat=60/bpm; bar=4*beat
def midi(m): return 440*2**((m-69)/12)
progs=[[57,53,48,55],[50,53,45,52]]  # Am F C G  /  Dm F Am Em
prog=progs[seed%2]
qual={57:[0,3,7],53:[0,4,7],48:[0,4,7],55:[0,4,7],50:[0,3,7],45:[0,3,7],52:[0,3,7]}
pad=np.zeros(n); bass=np.zeros(n); kick=np.zeros(n); hat=np.zeros(n); arp=np.zeros(n)
rng=np.random.default_rng(seed)
nb=int(np.ceil((dur+1.5)/bar))
for b in range(nb):
    root=prog[b%4]; s0=int(b*bar*sr); s1=min(n,int((b+1)*bar*sr)); tt=t[s0:s1]-b*bar
    env=np.minimum(1,tt/0.6)*np.minimum(1,(bar-tt)/0.4+0.2)
    for iv in qual[root]:
        f=midi(root+12+iv)
        for det in (-0.25,0.25):
            ff=f*2**(det/1200*8)
            pad[s0:s1]+=env*(np.sin(2*np.pi*ff*tt)+0.3*np.sin(4*np.pi*ff*tt)+0.12*np.sin(6*np.pi*ff*tt))
    for k in range(8):  # eighth-note bass
        a=int((b*bar+k*beat/2)*sr); e=min(n,a+int(beat/2*sr*0.9))
        if a>=n: break
        tt2=t[a:e]-t[a]; bass[a:e]+=np.sin(2*np.pi*midi(root-12)*tt2)*np.exp(-tt2*5)
    arpn=[0,7,12,15 if qual[root][1]==3 else 16,12,7,0,7]
    for k in range(8):
        a=int((b*bar+k*beat/2)*sr); e=min(n,a+int(0.3*sr))
        if a>=n: break
        tt2=t[a:e]-t[a]; f=midi(root+24+arpn[k]); arp[a:e]+=np.sin(2*np.pi*f*tt2)*np.exp(-tt2*9)
for k in range(int((dur+1.5)/beat)):
    a=int(k*beat*sr)
    if a>=n: break
    e=min(n,a+int(0.35*sr)); tt2=t[a:e]-t[a]
    ph=2*np.pi*np.cumsum(45+90*np.exp(-tt2*28))/sr
    kick[a:e]+=np.sin(ph)*np.exp(-tt2*9)
    h=int((k+0.5)*beat*sr); he=min(n,h+int(0.06*sr))
    if h<n:
        nz=rng.standard_normal(he-h); nz=np.diff(np.concatenate([[0],nz])); hat[h:he]+=nz*np.exp(-np.arange(he-h)/sr*60)
def lp(x,a):
    y=np.zeros_like(x); acc=0.0
    # vectorized one-pole via lfilter-like cumulative approach
    from itertools import accumulate
    return np.array(list(accumulate(x,lambda p,v:p+a*(v-p))))
pad=lp(pad,0.08)
mix=0.10*pad+0.30*bass+0.42*kick+0.05*hat+0.07*arp
# intro filter-ish fade and outro fade
fade=np.minimum(1,t/1.2)*np.clip((dur+0.3-t)/1.5,0,1)
mix*=fade; mix=mix[:int(sr*dur)]
mix=np.tanh(mix*1.4)/np.tanh(1.4); mix*=0.75/np.max(np.abs(mix))
st=np.stack([mix,np.roll(mix,int(0.012*sr))*0.95+mix*0.05],1)
w=wave.open(outp,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((st*32767).astype(np.int16).tobytes()); w.close()
