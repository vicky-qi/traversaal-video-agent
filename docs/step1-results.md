# Step 1 Results: Setup and Prototype

## Decision: use HyperFrames (keep Remotion as fallback)

Both tools rendered the same 6-second test clip (title, animated bar, fade) at 1920×1080, 30 fps, and the output looked the same.

| | HyperFrames v0.8.140 | Remotion v4 |
|---|---|---|
| License | Apache-2.0, free | Free only for teams of ≤3 people; collaborating teams' headcounts are combined. Our team plus Traversaal.ai almost certainly needs a paid license |
| Authoring format | Plain HTML + CSS + GSAP | React/TypeScript components |
| Built-in TTS | Yes: `hyperframes tts` (Kokoro-82M, local, free, 12 voices) | No; needs an outside service |
| Built-in QA | `hyperframes check` catches layout overlap, contrast, and runtime errors before render | No equivalent |
| Agent skills | Installed automatically to `~/.claude/skills/` | Available separately |
| 6s test render time | ~15s | ~19s |

`hyperframes check` caught a real bug in the first test (overlapping text) before we watched the video. That kind of automatic check is what an agent pipeline needs.

## 30-second prototype: done

`prototypes/step1-scene/renders/step1-scene.mp4`: 30.0s, 1080p, H.264 + AAC, narrated, with captions and visuals synced to each sentence.

Steps:
1. `scene.json` holds the scene: narration split into sentences, visual type, on-screen labels.
2. `python voiceover.py` runs TTS per sentence, measures each clip, joins them with 0.35s pauses, and writes start/end times back into `scene.json`. Took 15s.
3. `index.html` is the composition. Captions and step highlights are keyed to those times.
4. `npx hyperframes check`, then `npx hyperframes render`. Render took 21s.

## Hand-off format (each stage passes this on)

```json
{
  "voice": { "engine": "kokoro", "voice_id": "af_heart", "speed": 0.9, "pause_between_sentences_s": 0.35 },
  "scenes": [{
    "scene_id": "s01",
    "title": "...",
    "visual_type": "key_points",            // title | key_points | chart | quote | image
    "target_duration_s": 30,
    "narration": [{ "id": "n1", "text": "...", "on_screen": { "point": 1, "label": "..." } }],
    "sources": [],                          // filled by research and fact-check agents
    "audio": "assets/vo/s01.wav",           // filled by voiceover step
    "timing": { "lines": [{ "id": "n1", "start": 0.0, "end": 4.95 }], "audio_duration_s": 26.8 }
  }]
}
```

Rule: **audio is generated first, and visuals are timed to the measured audio**, never the other way around.

## Findings that affect the plan

- **Speaking pace is faster than planned.** Kokoro at 0.9× speed read 74 words in 26.8s, about 165 wpm including pauses (177 wpm while speaking). At this rate ~1,000 words is ~6 minutes, not 7. Either aim for ~1,150 words or slow the voice to 0.8×. Calibrate on a longer sample before you fix the script length.
- **Per-sentence TTS gives exact sync without transcription.** No Whisper needed.
- **Use one sub-composition file per scene in Step 3.** HyperFrames' checker recommends it, and it maps cleanly to "one scene = one file".
- **Cost so far: $0.** Everything runs locally on the M3 Mac.
- Kokoro's voice quality is fine for a prototype. Compare it to a paid voice (e.g. ElevenLabs) in Step 4 if narration scores are low.

## Environment (how to reproduce)

- Node 26, FFmpeg 9, Python 3.12, kokoro-onnx are all in the conda env `video` (`conda activate video`). Remove it with `conda env remove -n video`.
- TTS needs: `export HYPERFRAMES_PYTHON=$(which python)` after activating.
- HyperFrames telemetry disabled.

```bash
conda activate video
export HYPERFRAMES_PYTHON=$(which python)
cd prototypes/step1-scene
python voiceover.py
npx hyperframes check
npx hyperframes render --output renders/step1-scene.mp4 --quality delivery
```

## Folder

```
capstone-video/
  prototypes/hf-test/        HyperFrames 6s test clip   (renders/hf-test.mp4)
  prototypes/remotion-test/  Remotion 6s test clip      (out/remotion-test.mp4)
  prototypes/step1-scene/     30s narrated prototype     (renders/step1-scene.mp4)
```
