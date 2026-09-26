/* Generic scene engine: any topic as a list of scenes.
   STORY.videos[id] = {label, scenes:[{type, vo, ...}], timing:{d:[...]}}
   Scene types: hook, bignum, bullets, bars, line, compare, quote, reveal, steps, sources.
   Every scene reads only its own fields, so writers compose videos without touching code. */
function scenesVideo(id){
  const V=STORY.videos[id],SC=V.scenes,n=SC.length;
  const d=(V.timing&&V.timing.d)||SC.map(s=>s.dur||4.5);
  const T=[];let t0=0;d.forEach(x=>{T.push([t0,t0+x]);t0+=x-.3});const DUR=t0+.3;
  const X0=WIDE?170*S:64*S,CW=W-2*X0,TOP=WIDE?200*S:540*S,BOT=WIDE?H-120*S:H-380*S;
  const num=s=>{const m=String(s).match(/^([^\d−-]*)([−-]?)([\d,]*\.?\d+)(.*)$/);return m?{pre:m[1],neg:m[2],v:parseFloat(m[3].replace(/,/g,'')),dec:(m[3].split('.')[1]||'').length,comma:m[3].includes(','),suf:m[4]}:null};
  const fmtN=(p,v)=>{let s=v.toFixed(p.dec);if(p.comma)s=Number(s).toLocaleString('en-US',{minimumFractionDigits:p.dec,maximumFractionDigits:p.dec});return p.pre+p.neg+s+p.suf};
  function title(s,y,px=WIDE?56:66){if(!s)return y;const lh=px*1.15*S;font('SG',700,px);const lines=lines_(s,CW);lines.forEach((l,i)=>txt(l,X0,y+i*lh));return y+lines.length*lh}
  function lines_(s,w){const ws=String(s).split(' '),out=[];let ln='';for(const w0 of ws){const tl=ln?ln+' '+w0:w0;if(X.measureText(tl).width>w&&ln){out.push(ln);ln=w0}else ln=tl}out.push(ln);return out}
  function kicker(s,y){if(!s)return;font('IN',700,26);txt(String(s).toUpperCase(),X0,y,{c:C.amber,ls:4})}
  function note(s){if(!s)return;font('IN',500,WIDE?22:26);const ls=lines_(s,CW);ls.forEach((l,i)=>txt(l,X0,BOT+40*S+i*30*S,{c:C.dim}))}
  const IN=(lt,delay,dur=.5)=>out(clamp((lt-delay)/dur));
  const draw={
    hook(s,lt,D){
      const y=WIDE?420*S:760*S,x=WIDE?W/2:X0,al=WIDE?'center':'left';
      if(s.kicker){font('IN',700,26);txt(s.kicker.toUpperCase(),x,y-130*S,{c:C.amber,ls:4,al})}
      headline(s.lines||[s.text],x,y,WIDE?84:86,lt,{al,hl:s.hl||[]});
      if(s.sub){font('IN',500,34);txt(s.sub,x,y+(WIDE?230:250)*S,{c:C.mut,al,a:IN(lt,1.2)})}
    },
    bignum(s,lt,D){
      kicker(s.kicker||s.label,TOP);
      const p=num(s.value),k=IN(lt,.2,1.2);
      const shown=p?fmtN(p,p.v*k):s.value;
      fitFont('JB',700,WIDE?170:230,s.value,CW);X.save();X.globalAlpha*=IN(lt,.1,.4);txt(shown,X0,TOP+(WIDE?230:290)*S,{c:C[s.color]||C.green});X.restore();
      if(s.sub){font('IN',500,WIDE?38:48);X.save();X.globalAlpha*=IN(lt,.9);wrap(s.sub,X0,TOP+(WIDE?320:400)*S,CW,(WIDE?52:62)*S,C.ink);X.restore()}
      note(s.note);
    },
    bullets(s,lt,D){
      kicker(s.kicker,TOP);let y=title(s.title,TOP+70*S);y+=30*S;
      const items=s.items||[],gap=WIDE?18*S:26*S,step=Math.max(.5,(D-1.4)/Math.max(1,items.length));
      font('IN',500,WIDE?34:44);
      items.forEach((it,i)=>{const k=IN(lt,.5+i*step*.85);const txt0=typeof it==='string'?it:it.text,tag=typeof it==='string'?String(i+1):(it.tag||String(i+1));
        font('IN',500,WIDE?34:44);const LH=WIDE?48*S:56*S;const ls=lines_(txt0,CW-150*S),h=Math.max(110*S,ls.length*LH+48*S);
        X.save();X.globalAlpha*=k;X.translate((1-k)*50*S,0);X.fillStyle=C.tile;rr(X0,y,CW,h,16*S);X.fill();
        fitFont('JB',700,40,tag,110*S);txt(tag,X0+30*S,y+h/2+14*S,{c:C.amber});
        font('IN',500,WIDE?34:44);ls.forEach((l,j)=>txt(l,X0+140*S,y+(h-ls.length*LH)/2+LH*.78+j*LH));X.restore();y+=h+gap});
      note(s.note);
    },
    bars(s,lt,D){
      kicker(s.kicker,TOP);let y=title(s.title,TOP+70*S);y+=40*S;
      const it=s.items||[],mx=Math.max(...it.map(a=>Math.abs(+a[1])),1e-9),lw=WIDE?420*S:300*S,bw=CW-lw-200*S,rh=Math.min(WIDE?90*S:150*S,(BOT-y)/Math.max(1,it.length));
      it.forEach((a,i)=>{const k=ease(clamp((lt-.4-i*.18)/1.1));const v=+a[1],w=Math.abs(v)/mx*bw*k,yy=y+i*rh;
        fitFont('SG',700,WIDE?36:44,a[0],lw-20*S);txt(a[0],X0,yy+rh*.6);
        X.fillStyle=C[a[2]]||(v>=0?C.green:C.red);rr(X0+lw,yy+rh*.2,Math.max(w,3*S),rh*.55,8*S);X.fill();
        font('JB',700,WIDE?30:38);const lab=a[3]!==undefined?a[3]:fmtN({pre:s.prefix||'',neg:v<0?'−':'',dec:s.dec??1,comma:true,suf:s.unit||''},Math.abs(v)*k);txt(lab,X0+lw+w+14*S,yy+rh*.6,{c:C.ink,a:IN(lt,.6+i*.18)})});
      note(s.note);
    },
    line(s,lt,D){
      kicker(s.kicker,TOP);let y=title(s.title,TOP+70*S);y+=50*S;
      const P=s.points||[],vs=P.map(p=>+p[1]),mn=Math.min(...vs),mx=Math.max(...vs),pad=(mx-mn)*.12||1,h=BOT-y-60*S,w=CW-120*S;
      const px=i=>X0+i/(P.length-1)*w,py=v=>y+h-(v-mn+pad)/(mx-mn+2*pad)*h;
      X.strokeStyle=C.line;X.lineWidth=1*S;[mn,mx].forEach(v=>{X.beginPath();X.moveTo(X0,py(v));X.lineTo(X0+w,py(v));X.stroke();font('JB',500,22);txt((s.prefix||'')+v.toLocaleString('en-US',{maximumFractionDigits:s.dec??2})+(s.unit||''),X0+w+12*S,py(v)+8*S,{c:C.dim})});
      const k=ease(clamp((lt-.3)/(D*.6))),m=(P.length-1)*k;
      X.strokeStyle=C[s.color]||C.green;X.lineWidth=5*S;X.lineJoin='round';X.beginPath();
      for(let i=0;i<=Math.floor(m);i++){const xx=px(i),yy=py(vs[i]);i?X.lineTo(xx,yy):X.moveTo(xx,yy)}
      if(m%1&&Math.ceil(m)<P.length){const i=Math.floor(m),f=m-i;X.lineTo(lerp(px(i),px(i+1),f),lerp(py(vs[i]),py(vs[i+1]),f))}X.stroke();
      font('JB',500,22);P.forEach((p,i)=>{if(i<=m&&(i===0||i===P.length-1||P.length<=8))txt(p[0],px(i),y+h+36*S,{c:C.mut,al:i===0?'left':i===P.length-1?'right':'center'})});
      if(k>.98){const i=P.length-1;X.fillStyle=C.ink;X.beginPath();X.arc(px(i),py(vs[i]),8*S,0,7);X.fill();font('JB',700,34);txt(P[i][2]||String(vs[i]),px(i)-14*S,py(vs[i])-22*S,{al:'right'})}
      note(s.note);
    },
    compare(s,lt,D){
      kicker(s.kicker,TOP);let y=title(s.title,TOP+70*S);y+=40*S;
      const cw=(CW-40*S)/2;[s.left,s.right].forEach((hd,j)=>{const k=IN(lt,.3+j*.2);X.save();X.globalAlpha*=k;X.fillStyle=j?'rgba(242,181,68,.14)':C.tile;rr(X0+j*(cw+40*S),y,cw,90*S,14*S);X.fill();fitFont('SG',700,40,hd,cw-40*S);txt(hd,X0+j*(cw+40*S)+24*S,y+60*S,{c:j?C.amber:C.ink});X.restore()});
      y+=120*S;(s.rows||[]).forEach((r,i)=>{const k=IN(lt,.8+i*.35);X.save();X.globalAlpha*=k;font('IN',700,24);txt(r[0].toUpperCase(),X0,y+i*150*S,{c:C.mut,ls:2});
        [r[1],r[2]].forEach((v,j)=>{font('IN',500,WIDE?32:42);wrap(v,X0+j*(cw+40*S),y+i*150*S+56*S,cw-10*S,(WIDE?42:52)*S,C.ink)});X.restore()});
      note(s.note);
    },
    quote(s,lt,D){
      const y=WIDE?260*S:560*S;font('SG',700,160);txt('“',X0-10*S,y,{c:C.amber,a:IN(lt,0)});
      font('SG',500,WIDE?56:58);X.save();X.globalAlpha*=IN(lt,.2,.8);wrap(s.text,X0,y+60*S,CW,72*S,C.ink);X.restore();
      font('IN',500,30);txt('— '+(s.by||''),X0,BOT-40*S,{c:C.mut,a:IN(lt,1)});note(s.note);
    },
    reveal(s,lt,D){
      const at=s.at||D*.45;kicker(s.kicker||'GUESS',TOP);
      font('SG',700,WIDE?60:70);X.save();X.globalAlpha*=1-.6*IN(lt,at);wrap(s.question,X0,TOP+100*S,CW,(WIDE?76:84)*S,C.ink);X.restore();
      if(lt>at){const k=back(clamp((lt-at)/.6));X.save();X.translate(X0,TOP+(WIDE?430:520)*S);X.scale(.7+.3*k,.7+.3*k);fitFont('SG',700,WIDE?150:160,s.answer,CW);txt(s.answer,0,0,{c:C.amber});X.restore();
        if(s.sub){font('IN',500,WIDE?36:44);X.save();X.globalAlpha*=IN(lt,at+.5);wrap(s.sub,X0,TOP+(WIDE?520:640)*S,CW,(WIDE?48:56)*S,C.mut);X.restore()}}
      note(s.note);
    },
    steps(s,lt,D){ // numbered process with a connecting rail
      kicker(s.kicker,TOP);let y=title(s.title,TOP+70*S);y+=40*S;const it=s.items||[],step=Math.max(.6,(D-1.2)/Math.max(1,it.length)),rh=Math.min(WIDE?170*S:210*S,(BOT-y)/Math.max(1,it.length));
      X.strokeStyle='rgba(242,181,68,.35)';X.lineWidth=4*S;X.beginPath();X.moveTo(X0+34*S,y+34*S);X.lineTo(X0+34*S,y+34*S+(it.length-1)*rh*ease(clamp(lt/(D*.8))));X.stroke();
      it.forEach((a,i)=>{const k=IN(lt,.4+i*step*.8);X.save();X.globalAlpha*=k;X.fillStyle=C.amber;X.beginPath();X.arc(X0+34*S,y+34*S+i*rh,26*S,0,7);X.fill();
        font('JB',700,28);txt(String(i+1),X0+34*S,y+44*S+i*rh,{c:'#1b1405',al:'center'});
        font('SG',700,WIDE?38:48);txt(a[0],X0+90*S,y+48*S+i*rh);if(a[1]){font('IN',500,WIDE?28:36);wrap(a[1],X0+90*S,y+(WIDE?90:100)*S+i*rh,CW-90*S,(WIDE?38:46)*S,C.mut)}X.restore()});
      note(s.note);
    },
    sources(s,lt,D){
      const x=WIDE?W/2:X0,al=WIDE?'center':'left',y=WIDE?330*S:640*S;
      headline(s.lines||['Follow for more.'],x,y,WIDE?76:80,lt,{al,hl:s.hl||[]});
      if(s.sub){font('IN',500,32);txt(s.sub,x,y+(WIDE?150:190)*S,{c:C.mut,al})}
      font('IN',700,22);txt('SOURCES',WIDE?x-0:X0,y+(WIDE?230:280)*S,{c:C.amber,ls:3,al});
      font('IN',500,WIDE?22:26);let li=0;(s.list||[]).forEach(l=>lines_(l,CW).forEach(q=>txt(q,x,y+(WIDE?270:320)*S+(li++)*34*S,{c:C.dim,al})));
      if(s.disclaimer){font('IN',500,WIDE?22:26);txt(s.disclaimer,x,y+(WIDE?270:320)*S+li*34*S+24*S,{c:C.dim,al})}
    },
  };
  return {DUR,draw(t){bg(t);
    SC.forEach((s,i)=>{const [a,b]=T[i];const al=i===n-1?fadeIO(t,a,b+1):fadeIO(t,a,b);if(al<=0)return;X.save();X.globalAlpha=al;(draw[s.type]||draw.bullets)(s,t-a,d[i]);X.restore()});
    // scene dots
    const cy=WIDE?H-50*S:H-60*S;for(let i=0;i<n;i++){X.fillStyle=t>=T[i][0]?C.amber:'rgba(255,255,255,.14)';X.beginPath();X.arc(W/2+(i-(n-1)/2)*22*S,cy,5*S,0,7);X.fill()}
    brand(t,DUR,V.label||'CLIPS')}};
}
