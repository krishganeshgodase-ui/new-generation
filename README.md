# AutoShorts — AI YouTube Automation (free / local)

Enter a niche → the app writes an **original** script, records a voiceover, finds/generates visuals, edits a 9:16 Short with
captions, music and transitions, makes a thumbnail + title + description + tags, shows you a preview, and (after you authorise
YouTube) uploads it.

Everything runs on your PC. Costs ₹0: open-source tools plus free-tier APIs.

---------------------------------------------------------------------------------------------------

## 1. Install (Windows, from zero)

1. **Python 3.11+** — https://www.python.org/downloads/ (tick **"Add python.exe to PATH"** in the installer).
2. **FFmpeg** — open *PowerShell* and run:
   ```powershell
   winget install Gyan.FFmpeg
   ```
   Close and reopen PowerShell, then check: `ffmpeg -version`.
   (Mac: `brew install ffmpeg` · Linux: `sudo apt install ffmpeg`)
3. Put the project folder somewhere (e.g. `C:\ai_youtube_automation`) and run:
   ```powershell
   cd C:\ai_youtube_automation
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   copy .env.example .env
   python run.py
   ```
   Mac/Linux: `source venv/bin/activate` and `cp .env.example .env`.
4. `python run.py` prints a **setup check**, then opens the dashboard at http://127.0.0.1:8000.

```
 ✓ Python    ✓ FFmpeg    ✓ Database    ✓ TTS
 ⚠ YouTube API not configured      (fine for now — see section 4)
```
`✗` = must fix (the message tells you how). `⚠` = optional.

> **Linux only:** `pyttsx3` needs `sudo apt install espeak-ng`. On Windows it uses the built-in Windows voices.

## 2. Make your first video (TEST_MODE, no YouTube needed)

`.env` ships with `TEST_MODE=true`: everything is generated, **nothing is uploaded**.

1. Dashboard → **Create Video**.
2. Niche: `Funny AI Animal Stories`, leave Topic empty (the app invents the idea), Length `~40 sec`, Number of videos `1`.
3. Click **GENERATE VIDEOS** → watch progress on **Queue** (a 40 s video takes ~1–3 min on an average PC).
4. Open the video from the Dashboard → **VIDEO PREVIEW**: play it, edit title/description/script, regenerate script / voice / visuals / thumbnail.

Files land in `output/videos/video_001.mp4`, `output/thumbnails/thumbnail_001.png`, `output/audio/video_001.wav`.

## 3. Better scripts for free (strongly recommended)

Without a key the app uses **built-in offline templates** — they work, but the stories are generic. For real, original scripts add
*one* free option on the **Setup** page (or in `.env`):

| Option | Cost | How |
|---|---|---|
| **Gemini** | free tier | key from https://aistudio.google.com/apikey → `GEMINI_API_KEY` |
| **Groq** | free tier | https://console.groq.com/keys → `GROQ_API_KEY` |
| **Ollama** | free, local | install https://ollama.com, run `ollama pull llama3.2` — auto-detected |

Optional free stock photos: `PEXELS_API_KEY` (https://www.pexels.com/api/) or `PIXABAY_API_KEY`.

## 4. YouTube API credentials (one-time, ~10 min)

1. Go to https://console.cloud.google.com/ → create a **new project**.
2. *APIs & Services → Library* → search **YouTube Data API v3** → **Enable**.
3. *APIs & Services → OAuth consent screen* → User type **External** → fill the app name + your email →
   under **Test users** add **your own Google account** (the one that owns the channel) → Save.
4. *APIs & Services → Credentials → Create credentials → OAuth client ID* → Application type **Desktop app** → Create →
   **Download JSON**.
5. In the app: **Setup → YouTube → choose the JSON → Upload credentials**
   (or save it as `data/client_secret.json`).
6. Click **CONNECT YOUTUBE**. A Google page opens — pick your channel account, approve. (Google may warn the app is
   "unverified": click *Advanced → Continue*; it's your own app.) You never type your Google password into this app; only a
   revocable token is stored in `data/youtube_token.json`.

## 5. Go live

1. In `.env` set `TEST_MODE=false` and restart `python run.py`.
2. Preview a video → choose Privacy (start with **Private**) → optional **Schedule** → **Upload to YouTube**.
3. Or tick **Upload automatically** on the Create page.

## 6. Auto mode

**Auto Mode** page: e.g. *Generate 5 videos/day, upload 2/day at `12:00,19:00`.* Switch it **On**.
While the app is running it checks every minute. To run when the app window is closed, use Windows Task Scheduler:

```powershell
schtasks /Create /SC MINUTE /MO 15 /TN "AutoShorts" /TR "\"C:\ai_youtube_automation\venv\Scripts\python.exe\" \"C:\ai_youtube_automation\run.py\" tick"
```
`run.py tick` = one auto cycle + process the queue, then exit.

## 7. Customising

* **Your own images/video clips:** drop files in `assets/images/` (Visual source = Auto or "My media").
* **Music:** drop royalty-free `.mp3/.wav` in `assets/music/` — trimmed/looped, faded, and ducked under the voice automatically.
  Only use music you have the right to use.
* **Fonts:** drop `.ttf` files in `assets/fonts/` (used by thumbnails and captions).
* **Caption styles:** Clean / Bold / Gaming / Minimal; size, position and word-by-word highlight in Settings.

## 8. Project layout

```
run.py                  entry point (wizard / dashboard / `tick`)
app/main.py             FastAPI app + API        app/pipeline.py   stages & orchestration
app/queue.py            job queue + worker       app/auto.py       auto mode
app/ai/                 script, title, description generators + free LLM client
app/audio/tts.py        edge-tts → pyttsx3 → espeak-ng fallback chain
app/video/              scenes, visuals, captions (Whisper/ASS), editor (clips), renderer (final MP4)
app/thumbnails/         Pillow thumbnail generator
app/youtube/            OAuth (auth.py) and real resumable upload (uploader.py)
tests/                  pytest suite (`python -m pytest`)
```

## 9. Troubleshooting

Every failure shows *what / why / suggested fix* in the UI and in `logs/app.log`. Failed jobs resume from the failed stage via
**Retry** on the Queue page; other videos are never affected.

## 10. Honest limitations

* **Unverified YouTube API projects:** Google forces videos uploaded through *unaudited* API projects to **Private**. To publish
  publicly via API you must pass Google's API audit (https://support.google.com/youtube/contact/yt_api_form), or make the
  video public manually in YouTube Studio.
* **Quota:** the free API quota (10,000 units/day) allows ~**6 uploads/day**.
* **YouTube policies:** mass-produced, repetitive, low-effort content can be demonetised or removed ("inauthentic content"). The app
  marks uploads as AI-generated (Settings → *Mark as AI-generated*). Review videos before publishing, vary topics, add your own
  value. Quality of the offline template scripts is basic — use an LLM key.
* **Visuals** are still images with zoom/pan (or your clips), not generated video. "AI / generated" uses the free
  pollinations.ai image service when reachable and falls back to local abstract backgrounds.
* **edge-tts** (best free voices) needs internet; otherwise offline voices are used (more robotic).
* **Whisper** downloads a model (~150 MB for `base`) on first use; until then captions use script-based timing.
