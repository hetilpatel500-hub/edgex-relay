// usage: node shoot.js PORT VIDEO W H OUT.mp4
//        node shoot.js PORT VIDEO W H stills:PREFIX t1 t2 ...   (writes PREFIX.0.png, PREFIX.1.png, ...)
const {chromium}=require('playwright');const {spawn,execSync}=require('child_process');
const [port,v,w,h,mode,...times]=process.argv.slice(2);
const FF=process.env.FFMPEG||execSync("python3 -c 'import imageio_ffmpeg as i;print(i.get_ffmpeg_exe())'").toString().trim();
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h}});
 let err=null;p.on('pageerror',e=>{err=e;console.error('PAGE ERROR',e.message)});
 await p.goto(`http://127.0.0.1:${port}/render.html?v=${v}&w=${w}&h=${h}`);await p.evaluate(()=>window.ready);
 const dur=await p.evaluate(()=>window.DUR);
 if(mode.startsWith('stills:')){const pre=mode.slice(7);
   for(let i=0;i<times.length;i++){await p.evaluate(t=>{for(let k=0;k<40;k++)frame(t)},+times[i]);await p.screenshot({path:`${pre}.${i}.png`})}
   await b.close();if(err)process.exit(3);return}
 const fps=30,n=Math.round(dur*fps);
 const ff=spawn(FF,['-y','-loglevel','error','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',mode],{stdio:['pipe','inherit','inherit']});
 for(let i=0;i<n;i++){await p.evaluate(t=>frame(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:94});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%300==0)console.log(`${v} ${w}x${h} frame ${i}/${n}`)}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();
 if(err)process.exit(3);console.log(`done ${mode} ${dur}s`);
})().catch(e=>{console.error(e);process.exit(1)});
