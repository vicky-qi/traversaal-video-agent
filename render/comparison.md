# HyperFrames vs. Remotion

**Decision: HyperFrames, with Remotion as the fallback.**

The test projects and most of these findings come from Jiaxin's pipeline branch (`docs/step1-results.md`, `prototypes/`). The last section was confirmed again on Vicky's Mac on Oct 7 when building `render/`.

| | HyperFrames 0.8.140 | Remotion 4 |
|---|---|---|
| License | Apache-2.0, free | Free only for teams of up to 3 people, with collaborating teams' headcounts combined; our team plus Traversaal.ai almost certainly needs a paid company license |
| How scenes are written | Plain HTML + CSS + GSAP | React / TypeScript components |
| Text-to-speech | Built in: `hyperframes tts` (Kokoro-82M, runs locally, free, 12 voices) | None; needs an outside service |
| Automatic quality check | `hyperframes check`: layout overlap, text overflow, contrast, motion and runtime errors before rendering | No equivalent |
| Claude Code skills | `npx skills add heygen-com/hyperframes` | `npx skills add remotion-dev/skills` |
| 6-second test render (Jiaxin) | about 15 s | about 19 s |

Both produced the same-looking 1080p clip. HyperFrames wins on licence, built-in voice and the automatic check, which is what an unattended agent pipeline needs.

## Confirmed on Vicky's Mac (Apple M4)

- Voiceover for a 2-scene, 174-word script: about 30 s, local and free.
- Rendering the 65.7 s sample video (`runs/sample/final.mp4`) at standard quality: about 45 s.
- Voice `af_heart` at speed 0.85 reads about 145 words per minute, matching the script agent's target.
- `hyperframes check` caught two real template problems (motion on a layout property, a chart label outside its box) before they reached a video.

## Risks

- Kokoro's voice is good for a prototype; compare it with a paid voice (for example ElevenLabs) if narration scores are low. Jiaxin found numbers are read in full ("2025" becomes "twenty twenty-five"), which makes number-heavy lines longer.
- The templates load GSAP and the Inter font from the internet on first render; HyperFrames then caches them.
