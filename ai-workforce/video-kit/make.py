#!/usr/bin/env python3
"""Build finished videos from story.json: voiceover, timing, render, music,
mix, review sheets, a check report and the delivery page.

usage: make.py story.json OUT_DIR [--only spy|mag] [--no-wide]

Needs (run setup.sh once per machine): numpy, soundfile, sherpa-onnx,
imageio-ffmpeg, Pillow, Playwright + Chromium, and the Kokoro voice model
(KOKORO_DIR, default ~/.cache/edgex-kokoro/kokoro-int8-en-v0_19).
"""
import json, os, re, subprocess, sys, shutil, threading, functools, wave
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import numpy as np

KIT = os.path.dirname(os.path.abspath(__file__))
SR = 44100
VOICE = int(os.environ.get('EDGEX_VOICE_SID', '6'))  # Kokoro v0.19: 6 = am_michael
SPEED = float(os.environ.get('EDGEX_VOICE_SPEED', '1.12'))


def ffmpeg():
    if os.environ.get('FFMPEG'):
        return os.environ['FFMPEG']
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# ---------------- speech text normalisation ----------------
ONES = 'zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen'.split()
TENS = 'x x twenty thirty forty fifty sixty seventy eighty ninety'.split()


def words(n):
    n = int(n)
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ('' if n % 10 == 0 else '-' + ONES[n % 10])
    if n < 1000:
        return ONES[n // 100] + ' hundred' + ('' if n % 100 == 0 else ' ' + words(n % 100))
    if n < 1000000:
        return words(n // 1000) + ' thousand' + ('' if n % 1000 == 0 else ' ' + words(n % 1000))
    return str(n)


def two(d):  # "07" -> "oh seven", "10" -> "ten"
    return ('oh ' + ONES[int(d[1])]) if d[0] == '0' else words(int(d))


def say_price(ip, dp):
    n = int(ip)
    if 100 <= n < 1000 and n % 100:
        head = ONES[n // 100] + ' ' + (('oh ' + ONES[n % 100]) if n % 100 < 10 else words(n % 100))
    else:
        head = words(n)
    return head + ('' if dp is None else ' ' + (two(dp) if len(dp) == 2 else 'point ' + ' '.join(ONES[int(c)] for c in dp)))


def say_dec(ip, dp):
    return ('' if ip == '0' else words(ip) + ' ') + ('point ' + ' '.join(ONES[int(c)] for c in dp) if dp else '')


TICK = {'SPY': 'S P Y', 'QQQ': 'triple Q', 'VWAP': 'V-wap', 'AAPL': 'Apple', 'MSFT': 'Microsoft', 'NVDA': 'Nvidia',
        'GOOGL': 'Google', 'AMZN': 'Amazon', 'META': 'Meta', 'TSLA': 'Tesla', 'Mag 7': 'Mag Seven',
        'AI': 'A I', 'TPU': 'T P U', 'TPUs': 'T P Us', 'US': 'U S', 'NVDA ': 'Nvidia ', 'EPS': 'E P S', 'R&D': 'R and D'}


def speakable(s):
    s = s.replace('−', '-').replace('×', ' times ').replace('→', ' to ')
    for k, v in TICK.items():
        s = re.sub(r'\b' + re.escape(k) + r'\b', v, s)
    s = re.sub(r'\bET\b', '', s)
    s = re.sub(r'\$(\d+)\.(\d\d)\b', lambda m: (words(m.group(1)) + ' dollars ' if m.group(1) != '0' else '') +
               ('and ' if m.group(1) != '0' and m.group(2) != '00' else '') + (words(int(m.group(2))) + ' cents' if m.group(2) != '00' else ''), s)
    s = re.sub(r'([+-]?)(\d+)(?:\.(\d+))?%', lambda m: ('plus ' if m.group(1) == '+' else 'minus ' if m.group(1) == '-' else '') +
               say_dec(m.group(2), m.group(3)).strip() + ' percent', s)
    s = re.sub(r'\b(\d{1,2}):(\d\d)\b', lambda m: words(m.group(1)) + ' ' + ('' if m.group(2) == '00' else two(m.group(2))), s)
    s = re.sub(r'\b(\d{2,4})\.(\d{2})\b', lambda m: say_price(m.group(1), m.group(2)), s)
    s = re.sub(r'\b(\d+)\.(\d+)M\b', lambda m: say_dec(m.group(1), m.group(2)) + ' million', s)
    s = re.sub(r'\b(\d+)\.(\d+)\b', lambda m: say_dec(m.group(1), m.group(2)), s)
    s = re.sub(r'\b\d+\b', lambda m: words(m.group(0)), s)
    return re.sub(r'\s+', ' ', s).strip()


# ---------------- voice ----------------
_tts = None


def tts(text):
    global _tts
    import sherpa_onnx
    if _tts is None:
        M = os.environ.get('KOKORO_DIR', os.path.expanduser('~/.cache/edgex-kokoro/kokoro-int8-en-v0_19')) + '/'
        if not os.path.exists(M + 'model.int8.onnx'):
            sys.exit(f'Voice model not found in {M}. Run setup.sh first.')
        cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
            kokoro=sherpa_onnx.OfflineTtsKokoroModelConfig(model=M + 'model.int8.onnx', voices=M + 'voices.bin',
                                                           tokens=M + 'tokens.txt', data_dir=M + 'espeak-ng-data'),
            num_threads=max(2, os.cpu_count() or 2)))
        _tts = sherpa_onnx.OfflineTts(cfg)
    a = _tts.generate(speakable(text), sid=VOICE, speed=SPEED)
    x = np.asarray(a.samples, dtype=np.float32)
    if a.sample_rate != SR:
        n = int(len(x) * SR / a.sample_rate)
        x = np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)
    nz = np.nonzero(np.abs(x) > 0.01)[0]  # trim silence
    if len(nz):
        x = x[max(0, nz[0] - 800): nz[-1] + 2000]
    return x / (np.max(np.abs(x)) + 1e-9) * 0.9


# ---------------- timing (mirrors render.html) ----------------
def starts(d):
    t, out = 0, []
    for x in d:
        out.append(t); t += x - .3
    return out, t + .3


def plan_spy(st, vo):
    """Chart draws at a steady pace and pauses at each callout for its line."""
    N = len(st['spy']['rows'])
    clips = {'hook': tts(vo['hook']), 'marks': [tts(x) for x in vo['marks']], 'stats': tts(vo['stats']), 'outro': tts(vo['outro'])}
    L = lambda x: len(x) / SR
    PER_BAR = 0.11  # seconds per 5-minute candle while drawing
    warp, t, done, place = [[0.6, 0]], 0.6, 0, []
    for m, clip in zip(st['spy']['marks'], clips['marks']):
        stop = min(N, m['i'] + 1)
        t += (stop - done) * PER_BAR; done = stop
        warp.append([round(t, 3), stop]); place.append(t + 0.15)
        t += L(clip) + 0.45
        warp.append([round(t, 3), stop])
    if done < N:
        t += (N - done) * PER_BAR; warp.append([round(t, 3), N])
    d = [max(3.4, L(clips['hook']) + 0.9), t + 0.8, max(5.9, L(clips['stats']) + 1.2), max(3.6, L(clips['outro']) + 1.0)]
    s0, dur = starts(d)
    cues = [(0.25, clips['hook'])] + [(s0[1] + p, c) for p, c in zip(place, clips['marks'])] + \
           [(s0[2] + .45, clips['stats']), (s0[3] + .35, clips['outro'])]
    return d, dur, cues, warp


def plan_mag(vo):
    c = {k: tts(vo[k]) for k in ('hook', 'race', 'rev', 'outro')}
    L = lambda k: len(c[k]) / SR
    d = [max(3.6, L('hook') + 0.9), 15.3, max(6.3, L('rev') + 1.4), max(3.7, L('outro') + 1.0)]
    s0, dur = starts(d)
    return d, dur, [(0.25, c['hook']), (s0[1] + .4, c['race']), (s0[2] + .3, c['rev']), (s0[3] + .35, c['outro'])]


# ---------------- audio ----------------
def mix(dur, cues, seed, path):
    tmp = path + '.music.wav'
    subprocess.run([sys.executable, os.path.join(KIT, 'music.py'), f'{dur:.2f}', tmp, str(seed)], check=True)
    w = wave.open(tmp); mus = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32767; w.close(); os.remove(tmp)
    n = int(dur * SR); mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    voice = np.zeros(n, np.float32)
    for at, clip in cues:
        a = int(at * SR); b = min(n, a + len(clip)); voice[a:b] += clip[:b - a]
    env = np.convolve((np.abs(voice) > 0.02).astype(np.float32), np.ones(int(.25 * SR)) / int(.25 * SR), 'same')
    duck = 0.55 - 0.40 * np.clip(env * 3, 0, 1)
    outp = mus * duck[:, None] + voice[:, None] * 0.95
    outp = outp / max(1.0, np.max(np.abs(outp)) / 0.95)
    w = wave.open(path, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((outp * 32767).astype(np.int16).tobytes()); w.close()


# ---------------- render ----------------
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    srv = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=KIT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


def node():
    env = dict(os.environ)
    env.setdefault('NODE_PATH', '/opt/node22/lib/node_modules')
    return env


def render(port, v, w, h, outp):
    subprocess.run(['node', os.path.join(KIT, 'shoot.js'), str(port), v, str(w), str(h), outp], check=True, env=node())


def stills(port, v, w, h, times, outp):
    """Render frames at `times` and tile them into one review sheet."""
    from PIL import Image
    subprocess.run(['node', os.path.join(KIT, 'shoot.js'), str(port), v, str(w), str(h), 'stills:' + outp] + [f'{t:.2f}' for t in times],
                   check=True, env=node())
    parts = [outp + f'.{i}.png' for i in range(len(times))]
    tw = 360 if h > w else 640
    ims = [Image.open(p).resize((tw, int(tw * h / w))) for p in parts]
    cols = min(len(ims), 5 if h > w else 3)
    rows = -(-len(ims) // cols)
    sheet = Image.new('RGB', (cols * (tw + 8) - 8, rows * (ims[0].height + 8) - 8), 'white')
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * (tw + 8), (i // cols) * (im.height + 8)))
    sheet.save(outp)
    for p in parts:
        os.remove(p)


def probe(p):
    r = subprocess.run([ffmpeg(), '-hide_banner', '-i', p], capture_output=True, text=True).stderr
    d = re.search(r'Duration: (\d+):(\d+):([\d.]+)', r)
    v = re.search(r'Video: (\w+).*?, (\d+)x(\d+)', r)
    a = re.search(r'Audio: (\w+)', r)
    return dict(file=os.path.basename(p), bytes=os.path.getsize(p),
                seconds=round(int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)), 2) if d else None,
                video=f'{v.group(1)} {v.group(2)}x{v.group(3)}' if v else None, audio=a.group(1) if a else None)


def fit(p, limit):
    """Re-encode to a target bitrate when a file is over `limit` bytes."""
    if os.path.getsize(p) <= limit:
        return
    dur = probe(p)['seconds']
    kbps = int((limit * 8 / dur) / 1000 * 0.92) - 160
    tmp = p + '.fit.mp4'
    subprocess.run([ffmpeg(), '-hide_banner', '-loglevel', 'error', '-y', '-i', p, '-c:v', 'libx264', '-b:v', f'{kbps}k',
                    '-maxrate', f'{int(kbps*1.3)}k', '-bufsize', f'{kbps*2}k', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-c:a', 'copy', '-movflags', '+faststart', tmp], check=True)
    os.replace(tmp, p)
    print(f'fitted {os.path.basename(p)} to {os.path.getsize(p)/1e6:.1f} MB', flush=True)


def voice_level(p):
    r = subprocess.run([ffmpeg(), '-hide_banner', '-i', p, '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    m = re.search(r'mean_volume: ([-\d.]+)', r)
    return float(m.group(1)) if m else None


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    story_p, out = sys.argv[1], os.path.abspath(sys.argv[2])
    only = sys.argv[sys.argv.index('--only') + 1] if '--only' in sys.argv else None
    wide = '--no-wide' not in sys.argv
    os.makedirs(out, exist_ok=True)
    st = json.load(open(story_p))
    vids = [v for v in ('spy', 'mag') if v in st and (only in (None, v))]
    sess = st['spy']['session']
    st['timing'], cues = {}, {}
    for v in vids:
        print(f'[{v}] voiceover…', flush=True)
        warp = None
        if v == 'spy':
            d, dur, cu, warp = plan_spy(st, st['script']['spy']['vo'])
        else:
            d, dur, cu = plan_mag(st['script']['mag']['vo'])
        st['timing'][v] = dict(d=[round(x, 3) for x in d], dur=round(dur, 3))
        if warp:
            st['timing'][v]['warp'] = warp
        cues[v] = (dur, cu)
    with open(os.path.join(KIT, 'data.js'), 'w') as fh:
        fh.write('const STORY=' + json.dumps(st, ensure_ascii=False) + ';\n')
    port = serve()
    jobs, files = [], {}
    for v in vids:
        files[v] = {'tall': os.path.join(out, f'_{v}_tall.mp4')}
        jobs.append(threading.Thread(target=render, args=(port, v, 1080, 1920, files[v]['tall'])))
        if wide:
            files[v]['wide'] = os.path.join(out, f'_{v}_wide.mp4')
            jobs.append(threading.Thread(target=render, args=(port, v, 1920, 1080, files[v]['wide'])))
    print(f'rendering {len(jobs)} cuts…', flush=True)
    for j in jobs: j.start()
    for j in jobs: j.join()
    FF, final, report = ffmpeg(), {}, dict(session=sess, voice=f'Kokoro v0.19 sid {VOICE} speed {SPEED}', videos=[])
    for v in vids:
        dur, cu = cues[v]
        wav = os.path.join(out, f'_{v}.wav'); mix(dur, cu, 0 if v == 'spy' else 1, wav)
        for fmt, src in files[v].items():
            if not os.path.exists(src):
                sys.exit(f'render missing: {src}')
            dst = os.path.join(out, f'Edgex_{v}_{sess}_{"9x16" if fmt == "tall" else "16x9"}.mp4')
            subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', src, '-i', wav, '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
                            '-shortest', '-movflags', '+faststart', dst], check=True)
            final[(v, fmt)] = dst
        # review frames: one per scene plus each callout
        s0, _ = starts(st['timing'][v]['d'])
        d = st['timing'][v]['d']
        ts = [s0[0] + 1.8, s0[1] + d[1] * .45, s0[1] + d[1] - 1, s0[2] + d[2] - .8, s0[3] + d[3] - .3]
        if v == 'spy':
            ts += [at + .6 for at, _ in cu[1:-2]]
        stills(port, v, 1080, 1920, sorted(ts), os.path.join(out, f'review_{v}.png'))
        if wide:
            stills(port, v, 1920, 1080, sorted(ts)[:5], os.path.join(out, f'review_{v}_wide.png'))
        subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-ss', f'{s0[1] + d[1] * .7:.2f}', '-i', final[(v, 'tall')],
                        '-frames:v', '1', '-vf', 'scale=540:-1', '-q:v', '4', os.path.join(out, f'poster_{v}.jpg')], check=True)
    if wide and len(vids) > 1:
        yt = os.path.join(out, f'Edgex_recap_{sess}_16x9.mp4')
        subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', '-i', final[('spy', 'wide')], '-i', final[('mag', 'wide')],
                        '-filter_complex', '[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]', '-map', '[v]', '-map', '[a]',
                        '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                        '-movflags', '+faststart', yt], check=True)
        for v in vids:
            os.remove(final[(v, 'wide')]); del final[(v, 'wide')]
        final[('recap', 'wide')] = yt
    for p in [os.path.join(out, f) for f in os.listdir(out) if f.startswith('_')]:
        os.remove(p)
    for p in final.values():  # delivery page files must stay under 15 MB each
        fit(p, 14.0e6)
    for (v, fmt), p in sorted(final.items()):
        info = probe(p); info.update(kind=v, format=fmt, mean_volume_db=voice_level(p))
        report['videos'].append(info)
    report['voiceover'] = {v: [speakable(x) for x in ([st['script'][v]['vo']['hook']] + (st['script'][v]['vo']['marks'] if v == 'spy' else [st['script'][v]['vo']['race'], st['script'][v]['vo']['rev']]) +
                                               ([st['script'][v]['vo']['stats']] if v == 'spy' else []) + [st['script'][v]['vo']['outro']])] for v in vids}
    report['timing'] = st['timing']
    json.dump(report, open(os.path.join(out, 'report.json'), 'w'), indent=1, ensure_ascii=False)
    json.dump(st, open(os.path.join(out, 'story.final.json'), 'w'), indent=1, ensure_ascii=False)
    subprocess.run([sys.executable, os.path.join(KIT, 'page.py'), os.path.join(out, 'story.final.json'), os.path.join(out, 'report.json'), out], check=True)
    print(json.dumps(report['videos'], indent=1))


if __name__ == '__main__':
    main()
