// usage: node shoot.js v w h mode(out.mp4|stills) [times...]
const {chromium}=require('playwright');const {spawn}=require('child_process');
const [v,w,h,mode,...times]=process.argv.slice(2);
const FF=process.env.FFMPEG||require('child_process').execSync("python3 -c 'import imageio_ffmpeg as i;print(i.get_ffmpeg_exe())'").toString().trim();
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:+w,height:+h}});
 p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto(`http://127.0.0.1:8765/render.html?v=${v}&w=${w}&h=${h}`);await p.evaluate(()=>window.ready);
 const dur=await p.evaluate(()=>window.DUR);
 if(mode==='stills'){for(const t of times){await p.evaluate(t=>{window.__rk=null;frame(t)},+t);await p.screenshot({path:`st_${v}_${w}_${t}.png`})}await b.close();return}
 const fps=30,n=Math.round(dur*fps);
 const ff=spawn(FF,['-y','-f','image2pipe','-framerate',''+fps,'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',mode],{stdio:['pipe','inherit','inherit']});
 for(let i=0;i<n;i++){await p.evaluate(t=>frame(t),i/fps);const buf=await p.screenshot({type:'jpeg',quality:94});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));if(i%150==0)console.log(v,i,'/',n)}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('done',mode,dur);
})();
