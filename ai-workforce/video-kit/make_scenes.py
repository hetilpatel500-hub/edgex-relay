#!/usr/bin/env python3
"""Build any-topic videos from a scenes story (see FORMATS.md).

usage: make_scenes.py scenes.json OUT_DIR [--wide]

scenes.json = {"date": "YYYY-MM-DD",
               "videos": {"<id>": {"format": "<FORMATS.md id>", "label": "EXPLAINED",
                                    "caption": {"title": "...", "text": "..."},
                                    "sources": ["..."],
                                    "scenes": [{"type": "hook", "vo": "...", ...}, ...]}}}
Each scene's `vo` is spoken while it is on screen; a reveal scene can add `vo2`
spoken after the answer appears. Scene length follows the voice.
If OUT_DIR already has a report.json from make.py (the market videos), these
videos are appended to it and one delivery page covers everything.
"""
import json, os, sys, threading, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make  # voice, mixing, rendering helpers

SR = make.SR


def plan(v):
    d, cues, t = [], [], 0.0
    for s in v['scenes']:
        clip = make.tts(s['vo']) if s.get('vo') else None
        L = len(clip) / SR if clip is not None else 0
        dur = max(s.get('min', 3.2), L + 1.0)
        if s['type'] == 'reveal':
            s['at'] = round(L + 0.5, 2)
            clip2 = make.tts(s['vo2']) if s.get('vo2') else None
            L2 = len(clip2) / SR if clip2 is not None else 0
            dur = max(dur, s['at'] + 1.4 + L2)
            if clip2 is not None:
                cues.append((t + s['at'] + 0.6, clip2))
        if s['type'] in ('bullets', 'steps'):
            dur = max(dur, 1.4 + 0.9 * len(s.get('items', [])))
        if clip is not None:
            cues.append((t + 0.3, clip))
        d.append(round(dur, 3)); t += dur - .3
    return d, t + .3, cues


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    st = json.load(open(sys.argv[1])); out = os.path.abspath(sys.argv[2]); wide = '--wide' in sys.argv
    os.makedirs(out, exist_ok=True)
    cues = {}
    for vid, v in st['videos'].items():
        print(f'[{vid}] voiceover…', flush=True)
        d, dur, cu = plan(v)
        v['timing'] = {'d': d, 'dur': round(dur, 3)}
        cues[vid] = (dur, cu)
    data = f'data_{os.getpid()}.js'
    with open(os.path.join(make.KIT, data), 'w') as fh:
        fh.write('const STORY=' + json.dumps(st, ensure_ascii=False) + ';\n')
    os.environ['VK_DATA'] = data
    port = make.serve()
    jobs, files = [], {}
    for vid in st['videos']:
        files[(vid, 'tall')] = os.path.join(out, f'_{vid}_tall.mp4')
        jobs.append(threading.Thread(target=make.render, args=(port, vid, 1080, 1920, files[(vid, 'tall')])))
        if wide:
            files[(vid, 'wide')] = os.path.join(out, f'_{vid}_wide.mp4')
            jobs.append(threading.Thread(target=make.render, args=(port, vid, 1920, 1080, files[(vid, 'wide')])))
    print(f'rendering {len(jobs)} cuts…', flush=True)
    for j in jobs: j.start()
    for j in jobs: j.join()
    FF = make.ffmpeg(); final = {}
    for i, (vid, v) in enumerate(st['videos'].items()):
        dur, cu = cues[vid]
        wav = os.path.join(out, f'_{vid}.wav'); make.mix(dur, cu, i + 2, wav)
        for fmt in ('tall', 'wide'):
            src = files.get((vid, fmt))
            if not src:
                continue
            if not os.path.exists(src):
                sys.exit(f'render missing: {src}')
            dst = os.path.join(out, f'Edgex_{vid}_{st["date"]}_{"9x16" if fmt == "tall" else "16x9"}.mp4')
            subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-i', wav, '-c:v', 'copy', '-c:a', 'aac',
                            '-b:a', '160k', '-shortest', '-movflags', '+faststart', dst], check=True)
            final[(vid, fmt)] = dst
        # one review frame late in each scene
        ts, t = [], 0.0
        for x in v['timing']['d']:
            ts.append(t + x * 0.8); t += x - .3
        make.stills(port, vid, 1080, 1920, ts, os.path.join(out, f'review_{vid}.png'))
        subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{ts[min(1, len(ts)-1)]:.2f}', '-i', final[(vid, 'tall')],
                        '-frames:v', '1', '-vf', 'scale=540:-1', '-q:v', '4', os.path.join(out, f'poster_{vid}.jpg')], check=True)
    for f in os.listdir(out):
        if f.startswith('_'):
            os.remove(os.path.join(out, f))
    os.remove(os.path.join(make.KIT, data))
    for p in final.values():
        make.fit(p, 14.0e6)
    rp, sp = os.path.join(out, 'report.json'), os.path.join(out, 'story.final.json')
    rep = json.load(open(rp)) if os.path.exists(rp) else {'session': st['date'], 'videos': [], 'voiceover': {}, 'timing': {}}
    base = json.load(open(sp)) if os.path.exists(sp) else {'captions': {}, 'timing': {}}
    for (vid, fmt), p in sorted(final.items()):
        info = make.probe(p); info.update(kind=vid, format=fmt, mean_volume_db=make.voice_level(p), series=st['videos'][vid].get('format'))
        rep['videos'].append(info)
        rep['voiceover'][vid] = [make.speakable(s['vo']) for s in st['videos'][vid]['scenes'] if s.get('vo')] + \
                                [make.speakable(s['vo2']) for s in st['videos'][vid]['scenes'] if s.get('vo2')]
        rep['timing'][vid] = st['videos'][vid]['timing']
        cap = dict(st['videos'][vid]['caption'])
        if st['videos'][vid].get('sources'):
            cap['text'] = cap['text'].rstrip() + '\n\nSources: ' + '; '.join(st['videos'][vid]['sources'])
        base['captions'][vid] = cap
    json.dump(rep, open(rp, 'w'), indent=1, ensure_ascii=False)
    base.setdefault('scenes', {}).update(st['videos'])
    json.dump(base, open(sp, 'w'), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(make.KIT, 'page.py'), sp, rp, out], check=True)
    print(json.dumps([v for v in rep['videos'] if v['kind'] in st['videos']], indent=1))


if __name__ == '__main__':
    main()
