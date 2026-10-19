# Finance Advised — Shorts factory

This repo makes and publishes YouTube Shorts for the channel **Finance Advised** (@topfinanceadvised,
channel ID `UCPHtR3_kYJ3tBsAHDARGi6Q`). Every video is fully original: script, AI voice (Kokoro, voice
`af_heart`), code-drawn animation, synthesized music/SFX. No stock footage, no copyrighted music.

## Layout
- `setup.sh` — run once on a fresh machine. Builds espeak-ng and downloads the Kokoro voice model into `.tools/` (gitignored).
- `engine/` — templates: `tts_template.py` (voice + per-word timings), `mix_template.py` (music bed, ducking, SFX).
- `videos/NN-slug/` — one folder per video: `script.py` (SEGMENTS + numbers), `tts.py`, `render.py` (all visuals), `mix.py`.
  Copy the closest existing folder as a starting point (`06-same-raise` = latest WHO WINS? template), then restyle to the pillar's look.
- `queue/` — finished MP4s waiting to upload (served publicly at `https://raw.githubusercontent.com/lvprovisions-bot/finance-shorts/main/queue/<file>.mp4`).
- `published/log.csv` — every upload with its YouTube ID, pillar (`format`) and notes. Append rows with Python's csv module (titles contain commas — always quote).

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
- Three uploads per day (≈11:50, 16:50, 20:50 UK), at least 3 hours apart. With this volume every video MUST be a clearly different idea and look.

## Upload (via Zapier MCP, YouTube app, default connection)
- Every queued video is a pair: `queue/NN-slug.mp4` + `queue/NN-slug.json` with keys
  `title`, `description`, `format`, `length_s`, `category_id` ("27").
- Owner's decision (18-19 Oct 2026): fully automatic, **public**, three per day, no manual review.
- Commit + push the MP4 in `queue/` first so the raw URL resolves.
- `execute_zapier_write_action` YouTube `upload_video` with: `video` = raw URL, `title`, `description`, `category_id` "27",
  `made_for_kids` "false", `privacy_status` "public", `notify_subscribers` "true".
- Then `git mv queue/x.mp4 published/` is NOT needed — delete the MP4 from `queue/` in a follow-up commit to keep the repo small, and append the log row.
- After upload, post the channel's own first comment: a short, specific question that invites replies (pick a side,
  share a number, "go check yours"). Different wording every video. POST https://www.googleapis.com/youtube/v3/commentThreads?part=snippet
  via youtube_make_api_mutating_request with {"snippet":{"videoId":ID,"topLevelComment":{"snippet":{"textOriginal":TEXT}}}}.
  (The API can't pin comments; that's fine.) Never post more than one comment per video and never comment on other channels.
- Description template: story recap → takeaway line → comment question 👇 → "Follow for more numbers that change how you spend." → ⚠️ assumptions + "This is not financial advice." → 5–7 hashtags ending in #shorts.

## Long-form videos (weekly test, started 19 Oct 2026)
- Why: YPP's other route is 4,000 public watch hours/12 months (8,000 for new applicants from 1 Feb 2027); long-form also pays far more per view. Shorts stay at 3/day; a long video takes one of that day's 3 upload slots (the 3-hour guard handles it).
- Lives in `longform/` (NOT `queue/`; Shorts runs must never upload anything from `longform/`). Folder `videos/LNN-slug/` (copy `L01-rent-vs-buy`: model.py → script.py with {CAPTION|spoken} tokens → tts.py → render.py 1920x1080 scenes → mix.py → meta.py builds title/description with chapter timestamps; endcard_tts.py appends the logo + "watch our Shorts" end card).
- Topic choice is data-led: real decisions people search for, where SMALL channels (<100k subs) got 100k+ views in the current year (Zapier code action `topic_demand_analysis`). Queue of next topics: Leasing vs financing vs paying cash for a car; Index funds vs ETFs vs mutual funds (explain only, no fund picks).
- 8–15 min, US data with named official sources on screen and in the description, two cartoon characters + live scoreboard, honest "it depends" ending, comment question.
- Custom thumbnails need the owner's phone verification (youtube.com/verify) — until then the upload's thumbnail param fails but the video still uploads.

## Content pillars (styles) — rotate and let the data decide
Every video belongs to exactly ONE pillar. Each pillar has its own look so the channel feels varied (good for the
inauthentic-content rule) while each series is instantly recognisable. Put the pillar name in the log's `format` column.

| Pillar | Playlist ID | Idea | Look (must follow) | Hook pattern (frame 0) |
|---|---|---|---|---|
| **WHO WINS?** (proven) | `PLNjse90ClRp4` | Two fictional people, same money, different choices; payoff number reveal | Dark purple/blue gradient, two flat-colour cartoon people, yellow "WHO WINS?" headline, crown on winner | Both characters + "WHO WINS?" + the setup line |
| **THE REAL COST** | `PLM0WjUq_o4fo` | One everyday spend → what it really costs over years (invested or in interest) | Warm orange/amber, one big object icon (cup, phone, car, card), giant counting-up number | Object + "$X = $BIG" already on screen |
| **MONEY MYTHS: TRUE OR FALSE?** | `PLbgLGiiAALo8` | Test a popular belief with numbers; show BOTH sides fairly; verdict "it depends / mostly true / mostly false" | Teal/cyan + white, big quiz card with ✅/❌ stamp, split-screen pros/cons | Myth statement in quotes + "TRUE OR FALSE?" |
| **WOULD YOU RATHER?** | `PLJXCKLMm7Evk` | Two money options that seem obvious; maths reveals the surprise (e.g. $1M now vs a penny doubled daily for 30 days) | Black + bright yellow, A/B split screen, big "A" and "B" buttons, vote-style bars | "WOULD YOU RATHER" + both options on screen |
| **THEN VS NOW** | `PLZRTd10sBOsc` | What something cost in a past year vs today, and what that means (inflation, wages) | Retro sepia/green "receipt" or price-tag look, two dated cards side by side | Item + "THEN $X / NOW $Y" on screen |

Rules per pillar:
- **Myths**: present both sides; never tell viewers what to do; end with "it depends on…" + comment question.
- **Then vs Now**: every historical figure must come from an official/reputable source found with web search
  (e.g. US BLS CPI/average price data, UK ONS); name the source on screen ("Source: BLS") and in the description.
  If you can't source a number reliably, pick a different item.
- **Would You Rather**: compute exactly; state assumptions (rates, time) on screen.
- All pillars: 25–35 s, hook on screen + spoken from frame 0, loop back to the opening line, comment question.

**Slot rotation (default — the weekly review may change it):**
- 11:50 slot → WHO WINS? (proven winner).
- 16:50 and 20:50 slots → rotate through the other four pillars in order of whichever was used least recently
  (check `published/log.csv`), so each test pillar gets ~3–4 videos a week.
- Weekly review: a pillar that clearly beats the others (views per video, stayed-to-watch %) gets more slots;
  a pillar that's clearly worst after ≥4 videos is paused and replaced with a new pillar idea.

After uploading, add the video to its pillar's playlist (POST /youtube/v3/playlistItems).

## Thumbnails
- Make one for every video: write `thumbs/NN-slug.json` and run
  `python3 engine/thumbnail.py queue/NN-slug.mp4 thumbs/NN-slug.json thumbs/NN-slug.jpg`.
  Spec: `tag` = pillar name with the pillar's accent colour; 2–3 SHORT lines (max ~12 chars each) — the
  headline number contrast, e.g. ["SAME RAISE.", "$283K", "vs $0"]; green for gains, red for losses.
- Commit it, then try Zapier YouTube "Update Video Thumbnail" (tool_name youtube_update_video_thumbnail) with
  video_id + raw URL `https://raw.githubusercontent.com/lvprovisions-bot/finance-shorts/main/thumbs/NN-slug.jpg`.
- As of 19 Oct 2026 this FAILS with "doesn't have permissions to upload and set custom video thumbnails"
  (needs phone verification; Shorts custom thumbnails are rolling out to Partner Program channels first).
  If it fails with that message, skip quietly (do not raise ACTION NEEDED each time). The weekly review retries
  all un-applied thumbnails, and should report once if it starts working.
- Custom Shorts thumbnails don't show in the Shorts feed — frame 0 is still the feed "thumbnail", so keep the hook there.

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
- Max three uploads per UK calendar day, at least 3 hours apart, one per run.
- Thresholds (for context in reports): YPP = 1,000 subs + 10M Shorts views/90 days (or 4,000 watch hours/yr);
  from 1 Feb 2027 new applicants need 20M Shorts views/90 days (or 8,000 hours/yr). Fan-funding tier = 500 subs,
  3 uploads in 90 days, 3M Shorts views/90 days.

## Rules
- Never edit or delete a published video unless the owner asks. Never touch a video while it is being pushed (views climbing fast).
- Keep facts accurate and assumptions explicit. No guarantees of returns, no specific investment picks.
- Vary topics genuinely week to week (avoid looking mass-produced).
