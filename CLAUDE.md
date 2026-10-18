# Finance Advised — Shorts factory

This repo makes and publishes YouTube Shorts for the channel **Finance Advised** (@topfinanceadvised,
channel ID `UCPHtR3_kYJ3tBsAHDARGi6Q`). Every video is fully original: script, AI voice (Kokoro, voice
`af_heart`), code-drawn animation, synthesized music/SFX. No stock footage, no copyrighted music.

## Layout
- `setup.sh` — run once on a fresh machine. Builds espeak-ng and downloads the Kokoro voice model into `.tools/` (gitignored).
- `engine/` — templates: `tts_template.py` (voice + per-word timings), `mix_template.py` (music bed, ducking, SFX).
- `videos/NN-slug/` — one folder per video: `script.py` (SEGMENTS + numbers), `tts.py`, `render.py` (all visuals), `mix.py`.
  Copy the closest existing folder as a starting point. `04-twins` is the template for story videos.
- `queue/` — finished MP4s waiting to upload (served publicly at `https://raw.githubusercontent.com/lvprovisions-bot/finance-shorts/main/queue/<file>.mp4`).
- `published/log.csv` — every upload with its YouTube ID, format and notes. Append a row after each upload.

## Pipeline for one video
1. `./setup.sh` (skip if `.tools/` exists).
2. New folder `videos/NN-slug/`; write `script.py`. **Compute every number with Python first** and put the maths in the header comment.
3. `python3 tts.py` → `voice.wav`, `timings.json` (≈1 min on 2 cores). Check total length.
4. Write `render.py` acts; preview with `python3 render.py 0.0 3.0 ...` (writes `prev_*.png`), view a contact sheet, fix overlaps.
5. Sweep every 3rd frame for exceptions, then `python3 mix.py` and `python3 render.py`.
6. Mux: `ffmpeg -i video_noaudio.mp4 -i mix.wav -c:v copy -af "loudnorm=I=-14:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart queue/NN-slug.mp4`
7. Pull 8 frames from the final file and look at them before uploading.

Known pitfalls: never name a helper `g` (captions loop overwrites it); guard scale→0 in drawing helpers; font size must be ≥2.

## What works (update this as data comes in)
- **Two-character "who wins?" stories beat single calculations by ~10–20x** (04-twins). Default to this format.
- Target **25–35 seconds** (viewers left around 28–30 s of ~50 s videos).
- Hook must be **on screen and spoken from frame 0** (characters + "WHO WINS?" visible instantly, no pop-in, voice starts immediately).
- Ending should **loop** back into the opening line; end with a comment question ("Would you be Emma or Jack?").
- Bright accents on dark backgrounds, huge word-by-word captions (Poppins Bold, yellow active word, green for $ / %).
- Always show the on-screen assumptions disclaimer while numbers are shown, and put "not financial advice" in the description.
- One upload per day. Never post two within a few hours.

## Upload (via Zapier MCP, YouTube app, default connection)
- Commit + push the MP4 in `queue/` first so the raw URL resolves.
- `execute_zapier_write_action` YouTube `upload_video` with: `video` = raw URL, `title`, `description`, `category_id` "27",
  `made_for_kids` "false", `privacy_status` ("private" until the owner switches to auto-publish), `notify_subscribers` "true".
- Then `git mv queue/x.mp4 published/` is NOT needed — delete the MP4 from `queue/` in a follow-up commit to keep the repo small, and append the log row.
- Description template: story recap → takeaway line → comment question 👇 → "Follow for more numbers that change how you spend." → ⚠️ assumptions + "This is not financial advice." → 5–7 hashtags ending in #shorts.

## Analytics
Saved Zapier skill **"channel rundown"** pulls channel totals, per-video stats and YouTube Analytics
(views, engagedViews, averageViewDuration, averageViewPercentage). Analytics lag 24–48 h; say "not processed yet", not 0.
engagedViews ÷ views ≈ "stayed to watch".

## Monetisation rules (YouTube Partner Program) — MUST follow
Goal: stay eligible for YPP. Policy checked Oct 2026:
- YouTube's "inauthentic content" policy (clarified 16 Jul 2026) refuses monetisation to channels with too much
  **repetitive/generic content made easily with AI or templates with little variation between uploads**, or content
  **lacking a narrative arc**. So every video must:
  - have a real story/argument with a beginning, twist and payoff (two-character stories are ideal);
  - be a **genuinely new idea** — never re-skin a previous video with swapped numbers;
  - **vary the look**: rotate background palette, character designs/names, chart types and scene layouts so consecutive
    uploads don't look like one template (check the last 3 videos in `published/log.csv` before designing);
  - vary titles/description wording (no copy-paste boilerplate beyond the disclaimer).
- **No AI personas of real people**, and no fake "expert" presenter giving finance advice. Characters are clearly fictional
  cartoons; numbers are illustrations with stated assumptions. Never recommend specific stocks/products.
- No distressing or manipulative "rage/shock bait"; hooks may surprise but must be truthful.
- AI disclosure: the generic TTS narrator over cartoon graphics needs no "altered or synthetic" label. If a video ever uses
  photorealistic AI imagery, a realistic human voice clone, or generative-AI music, set the altered/synthetic disclosure.
- Never buy views/subscribers, use engagement pods, or delete-and-reupload to game the algorithm.
- Max one upload per day.
- Thresholds (for context in reports): YPP = 1,000 subs + 10M Shorts views/90 days (or 4,000 watch hours/yr);
  from 1 Feb 2027 new applicants need 20M Shorts views/90 days (or 8,000 hours/yr). Fan-funding tier = 500 subs,
  3 uploads in 90 days, 3M Shorts views/90 days.

## Rules
- Never edit or delete a published video unless the owner asks. Never touch a video while it is being pushed (views climbing fast).
- Keep facts accurate and assumptions explicit. No guarantees of returns, no specific investment picks.
- Vary topics genuinely week to week (avoid looking mass-produced).
