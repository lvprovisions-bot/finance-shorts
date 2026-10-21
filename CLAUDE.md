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
- **2-WEEK TEST (22 Oct – 4 Nov 2026), overrides the schedule/rotation below:** ONE Short a day at ≈18:50 UK. Only two pillars:
  WHO WINS? (Nora vs Theo story) and THEO EXPLAINS, alternating. 21–35 s, never longer. The first spoken sentence must be the
  conflict, joke or number itself (no set-up). Spend the time saved on quality: rewrite the first line 3 times and pick the strongest,
  and check frame 0 reads in under a second. No UK test, no other pillars, no long videos unless the owner sends a recording.
  Why: 17–21 Oct Shorts after the first spike got 0–23 views; stayed-to-watch 26–45%. Verdict on 4 Nov (scheduled task):
  continue only if ≥2 test Shorts pass 1,000 views or median stayed-to-watch ≥50%.
- **Two-character "who wins?" stories beat single calculations by ~10–20x** (04-twins). Default to this format.
- Target **21–35 seconds** (viewers left around 28–30 s of ~50 s videos). **Avoid 36–60 s**: worst length band in all 4 competitor groups (20 Oct audit, 24 channels).
- First sentence = the joke, conflict or number. No set-up line before it.
- Hook must be **on screen and spoken from frame 0** (characters + "WHO WINS?" visible instantly, no pop-in, voice starts immediately).
- Ending should **loop** back into the opening line; end with a comment question ("Would you be Emma or Jack?").
- Bright accents on dark backgrounds, huge word-by-word captions (Poppins Bold, yellow active word, green for $ / %).
- Always show the on-screen assumptions disclaimer while numbers are shown, and put "not financial advice" in the description.
- From 20 Oct 2026: **two Shorts a day (≈11:50, 20:50 UK)** + long-form Mon/Wed/Fri ≈16:00 UK; max 3 uploads/UK day, ≥3 h apart. Every video MUST be a clearly different idea and look.
- **UK test (from 21 Oct):** 2 of every 6 Shorts use £ and UK topics (only processed analytics: 100% UK viewers). Verify UK figures on GOV.UK.
- Audit doc with the 30-idea list and 30/90-day plan: https://claude.ai/code/artifact/3cc71a53-f65d-4a3d-af31-1c075518df07
- **Recurring cast (from 20 Oct): Nora & Theo** star in WHO WINS? and THEO EXPLAINS Shorts and in the long videos, so viewers recognise them
  and follow them from Shorts to long videos. Use the L01 designs (Nora: orange top, brown hair bun; Theo: teal/blue top, short dark hair)
  but vary poses, props, settings, palettes and layouts every video. Other pillars may use one-off characters.
  Evidence (19 Oct competitor scan): mascot-led channels win ("Ducky explains Taxes" 5.4M views, 21.7k subs from 19 videos;
  Mr Planktin 948k subs in 9 months); generic faceless tip channels flop (Capzeno 59 Shorts, median 275 views).
- **Big universal topics + humour/emotion beat narrow sums.** Prefer taxes, inflation, credit scores, interest, 401(k), insurance, debt.
- **Titles: under ~50 characters, plain words, max one emoji**. Hashtags in titles are allowed (no penalty in the 20 Oct audit data); "how/why/what" openers and the character's name did slightly better.
  e.g. "Theo Explains Taxes 😂", "Same Raise. One Is $283K Richer". 
- **Length test (from 21 Oct):** alternate 21–35 s and 61–90 s story Shorts (never 36–60 s); the weekly review decides from stayed-to-watch + avg % viewed.

## Upload (via Zapier MCP, YouTube app, default connection)
- Every queued video is a pair: `queue/NN-slug.mp4` + `queue/NN-slug.json` with keys
  `title`, `description`, `format`, `length_s`, `category_id` ("27").
- Owner's decision (18-19 Oct 2026): fully automatic, **public**, three per day, no manual review.
- Commit + push the MP4 in `queue/` first so the raw URL resolves.
- `execute_zapier_write_action` YouTube `upload_video` with: `video` = raw URL, `title`, `description`, `category_id` "27",
  `made_for_kids` "false", `privacy_status` "public", `notify_subscribers` "true".
- Then `git mv queue/x.mp4 published/` is NOT needed — delete the MP4 from `queue/` in a follow-up commit to keep the repo small, and append the log row.
- After upload, post the channel's own first comment: a short, specific question that invites replies (pick a side,
  share a number, "go check yours"). Different wording every video. POST https://www.googleapis.com/youtube/v3/commentThreads
  via youtube_make_api_mutating_request with querystring {"part":"snippet"} (putting ?part= in the URL fails with 400 unexpectedPart) and body {"snippet":{"videoId":ID,"topLevelComment":{"snippet":{"textOriginal":TEXT}}}}.
  (The API can't pin comments; that's fine.) Never post more than one comment per video and never comment on other channels.
- Description template: story recap → takeaway line → comment question 👇 → "Follow for more numbers that change how you spend." → ⚠️ assumptions + "This is not financial advice." → 5–7 hashtags ending in #shorts.

## Long-form videos (from 19 Oct 2026: 3 a week, NARRATED BY THE OWNER)
- Why: YPP's other route is 4,000 public watch hours/12 months; joining before **1 Feb 2027** keeps the old bar
  (8,000 h / 20M Shorts views for new applicants after that). From Feb 2027 Shorts only pay at 10M Shorts views/90 days,
  so long-form is the main money route. A human narrator is the strongest signal against the inauthentic-content policy.
- Schedule: Mon/Wed/Fri ≈15:45 UK (10:45am US East). Max 3 uploads/UK day overall, ≥3 h apart (Shorts at 11:50 and 20:50).
- Weekly flow:
  1. **Sunday task** ("Finance Advised: weekly long-video scripts") picks 3 data-backed topics, builds `videos/LNN-slug/`
     (model.py with sourced numbers → script.py with {CAPTION|spoken} tokens, short sentences written for a British narrator
     with a mild lisp: avoid dense "s" clusters) and puts a numbered recording script for each into the Drive folder
     **Finance Advised – voice** (`1KAU41CZ6pobXjmogT-Q_fHeO3DVo6_Vu`, channel account) as a Google Doc, then reports the links.
  2. The owner records each script as a phone voice memo and **sends it in the main Claude chat** (Drive downloads are not
     reachable from the build container, so recordings arrive as chat attachments).
  3. In that chat: `python3 engine/human_voice.py <memo> videos/LNN-slug` (clean-up + offline ASR + retake-aware matching →
     voice.wav + timings.json; exit 3 = paragraphs missing/unclear → ask the owner to re-record those numbers), then render.py,
     mix.py, mux to `longform/LNN-slug.mp4`, meta.py, thumb.py → `thumbs/LNN-slug.jpg`, upload at the next Mon/Wed/Fri slot.
- **Deadline plan (20 Oct):** https://claude.ai/code/artifact/b9442d9e-0748-478b-bf91-9073e200cebd — goal 1,000 subs + 4,000 eligible h, apply by 25 Jan 2027.
  Only long-form earns eligible hours. Long-video topics: prefer expanding a Short that beat the channel median (first: investing at 25 vs 35,
  from the twins Short), searchable "X or Y?" titles, payoff number in the first 15 s. Every long video gets a 21–35 s teaser Short within 24 h
  (WHO WINS?/THEO EXPLAINS look, ends "full breakdown on the channel"); the owner sets its Related video in Studio.
- Template: `videos/L02-lease-finance-cash` (owner voice; scenes.py style) or `L01-rent-vs-buy` (AI voice).
- Lives in `longform/` (NOT `queue/`; Shorts runs must never upload anything from `longform/`). Raw-URL upload, then thumbnail
  with youtube_update_video_thumbnail, playlist `PLTvjRc9qpEts`, seed comment, log row (format "LONG: ..."), delete the MP4.
- Topic choice is data-led: real decisions people search for, where SMALL channels (<100k subs) got 100k+ views this year
  (Zapier code action `topic_demand_analysis`). Topic queue: Savings account vs investing now rates are 4%+; Pay off your
  mortgage or invest?; Index funds vs ETFs vs mutual funds (explain only, no fund picks); 401(k) vs Roth IRA; Student loans
  after the SAVE plan; Is buy-now-pay-later a trap? (Black Friday 27 Nov); HSA vs FSA (open enrollment).
- 8–12 min, US data with named official sources on screen and in the description, Nora & Theo (+ guest), live scoreboard,
  honest "it depends" ending, comment question, logo + "watch our Shorts" end card (no narration on the end card).
- Custom thumbnails work (phone verified 19 Oct): 1280x720 JPEG, <2MB.

## Content pillars (styles) — rotate and let the data decide
Every video belongs to exactly ONE pillar. Each pillar has its own look so the channel feels varied (good for the
inauthentic-content rule) while each series is instantly recognisable. Put the pillar name in the log's `format` column.

| Pillar | Playlist ID | Idea | Look (must follow) | Hook pattern (frame 0) |
|---|---|---|---|---|
| **WHO WINS?** (proven) | `PLNjse90ClRp4` | Two fictional people, same money, different choices; payoff number reveal | Dark purple/blue gradient, two flat-colour cartoon people, yellow "WHO WINS?" headline, crown on winner | Both characters + "WHO WINS?" + the setup line |
| **THE REAL COST** | `PLM0WjUq_o4fo` | One everyday spend → what it really costs over years (invested or in interest) | Warm orange/amber, one big object icon (cup, phone, car, card), giant counting-up number | Object + "$X = $BIG" already on screen |
| **MONEY MYTHS: TRUE OR FALSE?** | `PLbgLGiiAALo8` | Test a popular belief with numbers; show BOTH sides fairly; verdict "it depends / mostly true / mostly false" | Teal/cyan + white, big quiz card with ✅/❌ stamp, split-screen pros/cons | Myth statement in quotes + "TRUE OR FALSE?" |
| **THEO EXPLAINS** (new 19 Oct) | `PLITIXxANiJ5g` | Theo confidently explains a big money topic (taxes, inflation, APR, credit score, 401k match, insurance deductible) and gets it hilariously wrong; Nora fixes it with one clear example and a number; punchline | Bright, playful: light pastel background that changes per episode, Theo & Nora large on screen, chalkboard/whiteboard prop with the key number, episode badge "THEO EXPLAINS #N" | Theo on screen saying the wrong claim + "THEO EXPLAINS: <TOPIC>" badge |
| **WOULD YOU RATHER?** | `PLJXCKLMm7Evk` | Two money options that seem obvious; maths reveals the surprise (e.g. $1M now vs a penny doubled daily for 30 days) | Black + bright yellow, A/B split screen, big "A" and "B" buttons, vote-style bars | "WOULD YOU RATHER" + both options on screen |
| ~~THEN VS NOW~~ (PAUSED 19 Oct: slow to source, weakest evidence) | `PLZRTd10sBOsc` | What something cost in a past year vs today, and what that means (inflation, wages) | Retro sepia/green "receipt" or price-tag look, two dated cards side by side | Item + "THEN $X / NOW $Y" on screen |

Rules per pillar:
- **Myths**: present both sides; never tell viewers what to do; end with "it depends on…" + comment question.
- **Then vs Now**: every historical figure must come from an official/reputable source found with web search
  (e.g. US BLS CPI/average price data, UK ONS); name the source on screen ("Source: BLS") and in the description.
  If you can't source a number reliably, pick a different item.
- **Would You Rather**: compute exactly; state assumptions (rates, time) on screen.
- All pillars: 25–60 s (see length test), hook on screen + spoken from frame 0, loop back to the opening line, comment question.

**Slot rotation (default — the weekly review may change it):**
- Two Short slots a day (11:50, 20:50 UK). One is WHO WINS? (proven), one rotates THEO EXPLAINS / THE REAL COST / MONEY MYTHS /
  WOULD YOU RATHER (least recently used first; THEO EXPLAINS gets at least 3 a week while it is new).
- Timing test: WHO WINS? alternates slots by UK date — even day-of-year → 11:50, odd → 20:50. The weekly review compares
  slots (11:50 UK = 6:50am US East, 20:50 = 3:50pm). Need ≥2 weeks before changing times. Never re-upload a video at another time.
- Topical Shorts: when a big scheduled money number is announced (e.g. 2027 401(k)/IRA limits, Fed decision, new tax brackets),
  the next slot may use it in any pillar, with the official source on screen.
- Weekly review: a pillar that clearly beats the others (views per video, stayed-to-watch %) gets more slots;
  a pillar that's clearly worst after ≥4 videos is paused and replaced with a new pillar idea.

After uploading, add the video to its pillar's playlist (POST /youtube/v3/playlistItems). Long videos go in `PLTvjRc9qpEts` ("The Money Maths (full videos)").

## Thumbnails
- Make one for every video: write `thumbs/NN-slug.json` and run
  `python3 engine/thumbnail.py queue/NN-slug.mp4 thumbs/NN-slug.json thumbs/NN-slug.jpg`.
  Spec: `tag` = pillar name with the pillar's accent colour; 2–3 SHORT lines (max ~12 chars each) — the
  headline number contrast, e.g. ["SAME RAISE.", "$283K", "vs $0"]; green for gains, red for losses.
- Commit it, then try Zapier YouTube "Update Video Thumbnail" (tool_name youtube_update_video_thumbnail) with
  video_id + raw URL `https://raw.githubusercontent.com/lvprovisions-bot/finance-shorts/main/thumbs/NN-slug.jpg`.
- WORKS since 19 Oct 2026 (owner verified their phone): apply the thumbnail after every upload. If it ever fails, report it.
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
  - **vary the look**: rotate background palette, character designs/names (except the recurring Nora & Theo), chart types and scene layouts so consecutive
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
