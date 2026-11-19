#!/usr/bin/env python3
"""Write the private delivery page (index.html) next to the finished MP4s.

usage: page.py story.final.json report.json OUT_DIR
Publish OUT_DIR/index.html as a new Artifact with capabilities {"downloads": true}
and every MP4 + poster_*.jpg in OUT_DIR as supporting files.
"""
import json, sys, os, html
from datetime import date

st, rep, out = json.load(open(sys.argv[1])), json.load(open(sys.argv[2])), sys.argv[3]
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
d = date.fromisoformat(rep['session'])
dl = f"{MON[d.month-1]} {d.day}"
E = html.escape
STYLE = '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap">\n<style>\n:root{\n  color-scheme:dark;\n  --bg:#0b1214;--panel:#111d1c;--panel2:#16262a;--ink:#eef3f1;--mut:#9aaca7;--dim:#5f736e;\n  --line:rgba(170,200,190,.14);--amber:#f2b544;--green:#35d39a;--red:#ff6a5c;--focus:#f2b544;\n  --display:"Space Grotesk",system-ui,sans-serif;--body:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;--mono:"JetBrains Mono",ui-monospace,Menlo,monospace;\n}\n*{box-sizing:border-box}\nbody{background:var(--bg);color:var(--ink);font:15px/1.55 var(--body);margin:0;padding-inline:16px;padding-block:28px 56px}\n.wrap{max-width:1120px;margin:0 auto;display:grid;gap:28px}\nheader{display:grid;gap:10px;padding-bottom:18px;border-bottom:1px solid var(--line)}\n.brand{display:flex;align-items:center;gap:10px;font:700 14px var(--display);letter-spacing:.2em}\n.brand svg{width:22px;height:18px}\n.brand span{color:var(--mut);font-weight:500}\nh1{font:700 clamp(28px,5vw,44px)/1.08 var(--display);margin:0;text-wrap:balance}\n.lede{color:var(--mut);max-width:65ch;margin:0}\n.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,500px),1fr));gap:20px}\n.clip{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:16px;display:grid;grid-template-columns:minmax(0,210px) 1fr;gap:18px;align-items:start}\n.clip.wide{grid-template-columns:1fr;grid-column:1/-1}\n@media (max-width:560px){.clip{grid-template-columns:1fr}}\nvideo{width:100%;max-width:100%;border-radius:10px;background:#000;display:block}\n.v916{aspect-ratio:9/16}.v169{aspect-ratio:16/9}\n.meta{display:grid;gap:10px;min-width:0}\n.tags{display:flex;flex-wrap:wrap;gap:6px}\n.tag{font:500 12px var(--mono);color:var(--amber);border:1px solid rgba(242,181,68,.35);border-radius:999px;padding:2px 10px}\n.tag.plain{color:var(--mut);border-color:var(--line)}\nh2{font:700 21px/1.2 var(--display);margin:0;text-wrap:balance}\n.facts{margin:0;color:var(--mut);font-size:14px}\n.facts b{color:var(--ink);font-weight:600}\n.cap{background:var(--panel2);border-radius:10px;padding:12px 14px;font-size:14px;white-space:pre-wrap;overflow-wrap:anywhere;color:#d6e0dd}\n.row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}\nbutton{font:600 14px var(--body);border-radius:9px;padding:9px 14px;cursor:pointer;border:1px solid var(--line);background:transparent;color:var(--ink)}\nbutton.save{background:var(--amber);color:#1b1405;border-color:var(--amber)}\nbutton:hover{filter:brightness(1.08)}\nbutton:focus-visible{outline:3px solid var(--focus);outline-offset:2px}\n.status{font-size:13px;color:var(--mut)}\n.num{font-family:var(--mono);font-variant-numeric:tabular-nums}\n.notes{display:grid;gap:8px;color:var(--mut);font-size:14px;max-width:75ch}\n.notes h3{font:700 15px var(--display);color:var(--ink);margin:0;letter-spacing:.04em}\n.notes ul{margin:0;padding-left:18px;display:grid;gap:4px}\n@media (prefers-reduced-motion:reduce){*{transition:none!important}}\n</style>'
SCRIPT = "<script>\nfunction statusFor(btn){return btn.parentElement.querySelector('.status')}\ndocument.querySelectorAll('button[data-copy]').forEach(btn=>{\n  btn.addEventListener('click',async()=>{\n    const el=document.getElementById(btn.dataset.copy);const st=statusFor(btn);\n    try{await navigator.clipboard.writeText(el.textContent);st.textContent='Copied'}\n    catch(e){const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);st.textContent='Selected. Press Ctrl+C or ⌘C to copy'}\n  });\n});\nlet dlP=null;\nfunction downloads(){if(!dlP)dlP=(window.claude&&window.claude.use)?window.claude.use('downloads').catch(()=>null):Promise.resolve(null);return dlP}\ndocument.querySelectorAll('button.save').forEach(btn=>{\n  btn.addEventListener('click',async()=>{\n    const st=statusFor(btn);btn.disabled=true;st.textContent='Preparing file…';\n    try{\n      const dl=await downloads();\n      if(!dl){st.textContent='Saving is not available in this view. Open the page on claude.ai to save.';return}\n      const blob=await (await fetch(btn.dataset.file)).blob();\n      await dl.save({filename:btn.dataset.file,data:blob});\n      st.textContent='Saved';\n    }catch(e){\n      const c=e&&e.code;\n      st.textContent=c==='declined'?'Save cancelled':c==='rate_limited'?'Another save is open. Try again in a moment.':'Could not save here. Open the page on claude.ai and try again.';\n    }finally{btn.disabled=false}\n  });\n});\n</script>\n"


def mmss(s):
    s = int(round(s)); return f"{s//60}:{s%60:02d}"


cards = []
for i, v in enumerate(rep['videos']):
    kind, tall = v['kind'], v['format'] == 'tall'
    cap = st['captions'].get('spy' if kind == 'recap' else kind, {})
    if kind == 'recap':
        sp, mg = st['captions']['spy'], st['captions']['mag']
        spy_len = st['timing']['spy']['dur']
        title = f"Market recap {dl}: {sp['title'].split(': ', 1)[-1]} + {mg['title']}"
        text = (f"{sp['text'].split(chr(10))[0]}\n\n{mg['text'].split(chr(10))[0]}\n\n"
                f"0:00 SPY session, candle by candle\n{mmss(spy_len)} Magnificent 7: this week\n\n"
                "Data: Webull. Educational only, not financial advice.")
    else:
        title, text = cap.get('title', ''), cap.get('text', '')
    poster = f"poster_{kind}.jpg" if os.path.exists(os.path.join(out, f"poster_{kind}.jpg")) else ''
    cards.append(f"""
    <article class="clip{'' if tall else ' wide'}">
      <video class="{'v916' if tall else 'v169'}" src="{E(v['file'])}" {f'poster="{poster}"' if poster and tall else ''} controls playsinline preload="metadata"></video>
      <div class="meta">
        <div class="tags"><span class="tag">{'9:16 SHORT' if tall else '16:9 VIDEO'}</span><span class="tag plain num">{mmss(v['seconds'])}</span><span class="tag plain">{'Reels · Shorts · TikTok' if tall else 'YouTube · Facebook'}</span><span class="tag plain">{E((v.get('series') or kind).replace('-',' '))}</span></div>
        <h2>{E(title)}</h2>
        <div class="cap" id="cap-{i}">{E(text)}</div>
        <div class="row"><button class="save" data-file="{E(v['file'])}">Save MP4 · {v['bytes']/1e6:.1f} MB</button><button data-copy="cap-{i}">Copy caption</button><span class="status" role="status"></span></div>
      </div>
    </article>""")

doc = f"""<title>Edgex Video Drop {dl}</title>
{STYLE}
<div class="wrap">
  <header>
    <div class="brand"><svg viewBox="0 0 34 28" aria-hidden="true"><path d="M0 0h22l12 14-12 14H0l12-14z" fill="#f2b544"/></svg>EDGEX <span>MARKETS</span></div>
    <h1>Video drop · {E(dl)}</h1>
    <p class="lede">Made by the Edgex video desk, voiced and checked by Video Last Touch before it reached you. Each video has a caption ready to paste and a Save button for the MP4.</p>
  </header>
  <div class="grid">{''.join(cards)}
  </div>
  <section class="notes">
    <h3>HOW THESE WERE MADE</h3>
    <ul>
      <li>Every number and claim traces to its source: Webull data, or the outlets named in each caption. The Video Fact-Checker checked each one before release.</li>
      <li>The voice is Kokoro, an open-source neural voice (Apache-2.0), rendered on the build machine. The music is synthesized for each video. There is no third-party footage.</li>
      <li>Nothing has been posted. You post these.</li>
    </ul>
  </section>
</div>
{SCRIPT}"""
open(os.path.join(out, 'index.html'), 'w').write(doc)
print('page written:', os.path.join(out, 'index.html'))
