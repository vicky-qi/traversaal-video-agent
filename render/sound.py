"""Sound stage for film mode: add a music bed and sound effects under the voiceover.

Called by render/render.py after the scenes are joined. Everything is synthesised with FFmpeg
(no downloads, no licences needed): a slow pad chord progression chosen by the storyboard's
music.mood, and short effects (whoosh, hit, rise, chime) placed at the start of every shot whose
`sound` asks for one. The music is ducked under the voice with a sidechain compressor.

Standalone test: render/env.sh python render/sound.py runs/<slug>   (uses build/joined.mp4)
"""
import json
import subprocess
import sys
from pathlib import Path

RATE = 48000
CHORD_SEC = 8.0
# Chord progressions (Hz): root an octave below plus a triad, per mood.
NOTE = {"A2": 110.0, "C3": 130.81, "D3": 146.83, "E3": 164.81, "F2": 87.31, "F3": 174.61, "G2": 98.0, "G3": 196.0,
        "A3": 220.0, "B3": 246.94, "C4": 261.63, "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "Bb2": 116.54, "Bb3": 233.08}
PROGRESSIONS = {
    "calm":      [["A2", "A3", "C4", "E4"], ["F2", "F3", "A3", "C4"], ["C3", "C4", "E4", "G4"], ["G2", "G3", "B3", "D4"]],
    "curious":   [["D3", "D4", "F4", "A3"], ["Bb2", "Bb3", "D4", "F4"], ["F2", "F3", "A3", "C4"], ["C3", "C4", "E4", "G3"]],
    "tense":     [["A2", "A3", "C4", "E4"], ["A2", "A3", "C4", "F4"], ["G2", "G3", "Bb3", "D4"], ["E3", "E4", "G3", "B3"]],
    "uplifting": [["C3", "C4", "E4", "G4"], ["G2", "G3", "B3", "D4"], ["A2", "A3", "C4", "E4"], ["F2", "F3", "A3", "C4"]],
}
SFX = {
    "whoosh": "anoisesrc=d=0.9:c=pink:a=0.6:r={r},highpass=f=500,lowpass=f=5000,afade=t=in:d=0.35,afade=t=out:st=0.35:d=0.55",
    "hit": "aevalsrc='0.9*sin(2*PI*55*t)*exp(-7*t)+0.25*sin(2*PI*110*t)*exp(-9*t)':d=0.9:s={r}",
    "rise": "aevalsrc='0.35*sin(2*PI*(180+260*t)*t)*min(1,t/0.9)':d=1.2:s={r},afade=t=out:st=0.9:d=0.3",
    "chime": "aevalsrc='0.28*(sin(2*PI*880*t)+0.6*sin(2*PI*1320*t))*exp(-3*t)':d=1.6:s={r}",
}


def run(cmd):
    subprocess.run(cmd, check=True)


def music_bed(out, seconds, mood, work):
    chords = PROGRESSIONS.get(mood, PROGRESSIONS["calm"])
    parts = []
    for i, chord in enumerate(chords):
        freqs = [NOTE[n] for n in chord]
        expr = "+".join(f"{0.10 if j == 0 else 0.07}*sin(2*PI*{f}*t)" for j, f in enumerate(freqs))
        expr = f"({expr})*(0.8+0.2*sin(2*PI*0.15*t))"
        part = work / f"chord{i}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"aevalsrc='{expr}':d={CHORD_SEC}:s={RATE}",
             "-af", "afade=t=in:d=1.5,afade=t=out:st=6.0:d=2.0", str(part)])
        parts.append(part)
    loop = work / "loop.wav"
    # Cross-fade the four chords into one loop.
    inputs = sum((["-i", str(p)] for p in parts), [])
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
         "[0][1]acrossfade=d=1.5[a];[a][2]acrossfade=d=1.5[b];[b][3]acrossfade=d=1.5[c]", "-map", "[c]", str(loop)])
    run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(loop), "-t", f"{seconds:.3f}",
         "-af", f"lowpass=f=1800,aecho=0.6:0.5:60|180:0.25|0.15,afade=t=in:d=3,afade=t=out:st={max(seconds - 4, 0):.3f}:d=4",
         "-ac", "1", "-ar", str(RATE), str(out)])


def sfx_track(out, seconds, cues, work):
    """cues: list of (time_sec, kind). Writes one mono track with every effect at its time."""
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=mono", "-t", f"{seconds:.3f}", str(out)])
    if not cues:
        return
    files = {}
    for kind in {k for _, k in cues}:
        f = work / f"sfx_{kind}.wav"
        run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", SFX[kind].format(r=RATE), "-ac", "1", str(f)])
        files[kind] = f
    inputs, chains = ["-i", str(out)], []
    for i, (t, kind) in enumerate(cues, 1):
        inputs += ["-i", str(files[kind])]
        ms = int(t * 1000)
        chains.append(f"[{i}]adelay={ms}|{ms},volume=0.55[s{i}]")
    mix_in = "[0]" + "".join(f"[s{i}]" for i in range(1, len(cues) + 1))
    tmp = work / "sfx_tmp.wav"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
         ";".join(chains) + f";{mix_in}amix=inputs={len(cues) + 1}:normalize=0:duration=first[o]",
         "-map", "[o]", "-t", f"{seconds:.3f}", str(tmp)])
    tmp.replace(out)


def cues_from_storyboard(board, timing):
    from render import film_shots  # same shot timing as the renderer
    cues, offset = [], 0.0
    for bs in board["scenes"]:
        t = timing[f"scene_{int(bs['id']):02d}"]
        for sh in film_shots(bs, t):
            if sh["sound"] and sh["sound"] != "none":
                cues.append((offset + sh["start"], sh["sound"]))
        offset += t["duration"]
    return cues, offset


def mix(run_dir, joined, final, board, timing):
    work = Path(run_dir) / "build" / "sound"
    work.mkdir(parents=True, exist_ok=True)
    cues, total = cues_from_storyboard(board, timing)
    music, sfx = work / "music.wav", work / "sfx.wav"
    music_bed(music, total, (board.get("music") or {}).get("mood", "calm"), work)
    sfx_track(sfx, total, cues, work)
    # Voice from the joined video; music ducked under the voice; effects on top; limiter at the end.
    run(["ffmpeg", "-v", "error", "-y", "-i", str(joined), "-i", str(music), "-i", str(sfx), "-filter_complex",
         "[0:a]aresample=48000,asplit=2[v1][v2];"
         "[1:a]volume=0.75[m];[m][v1]sidechaincompress=threshold=0.02:ratio=12:attack=20:release=450[duck];"
         "[v2][duck][2:a]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[a]",
         "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])
    print(f"  sound: music bed ({(board.get('music') or {}).get('mood', 'calm')}) + {len(cues)} sound effects mixed under the voice")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    r = Path(sys.argv[1]).resolve()
    b = json.loads((r / "05_storyboard.json").read_text())
    tm = json.loads((r / "audio" / "timing.json").read_text())["scenes"]
    mix(r, r / "build" / "joined.mp4", r / "final.mp4", b, tm)
