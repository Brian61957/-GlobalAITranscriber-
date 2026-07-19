# Global AI Transcriber — Streamlit Community Cloud Deployment

## What was fixed in this copy

1. **Headless browser** — `browser/browser_manager.py` and `ui/browser_process.py` now
   launch Chromium with `headless=True` instead of `headless=False`. Cloud servers have
   no display, so this is required for it to run there at all.
2. **`app.py` now installs Chromium itself on first boot** — Streamlit Cloud has no
   shell post-install hook, so a `st.cache_resource`-wrapped function runs
   `playwright install chromium` once per container. This is what was missing last
   time, causing the `Executable doesn't exist` error.
3. **`app.py` bridges Streamlit Secrets into `os.environ`** — so your existing
   `os.getenv("OPENAI_API_KEY")`-style code keeps working when the key is set via
   Streamlit Cloud's Secrets panel instead of a committed `.env`.
4. **Linux-friendly `requirements.txt`** — `torch` and `pyannote.audio` removed (they
   aren't actually imported anywhere, only mentioned in a comment, and are a common
   source of install failures on Streamlit Cloud).
5. **`packages.txt` added** — the Linux system libraries Chromium needs to run headless.
6. **Speaker-labeling bug fixed** — `speech/transcript_reviewer.py` was computing the
   speaker-labeled text (`Speaker 1: ...`, `Speaker 2: ...`) but never writing it back
   to `transcript.text`, so it silently never appeared in the output even though the
   app reported "Speaker labels applied." Now fixed — the labeled text is saved.
   Note: speaker labeling only works with the **Faster-Whisper** provider (the default),
   since that's the only one that returns segment timestamps; the GPT-4o Transcribe
   (OpenAI) provider doesn't currently supply the data it needs.
7. **`.gitignore` added** — keeps `.env`, saved Intron login sessions, audio files, and
   logs out of GitHub.
8. **Automated Intron login added** — the original app assumed a human would watch a
   *visible* browser window and log in manually (`ui/browser_process.py` literally
   waited up to 5 minutes for someone to click through a login form that, on headless
   cloud hosting, nobody can see). It now tries `INTRON_EMAIL` / `INTRON_PASSWORD`
   (from env/secrets) with Playwright first, and only falls back to the old
   wait-and-hope behavior if those aren't set or the automated attempt fails.

   **Important limitation:** this only works if Intron's login is a plain email +
   password form. If Intron requires a CAPTCHA, an emailed verification code, or 2FA,
   no amount of automation can get past that — a human genuinely has to be there. If
   you hit that wall, the real options are a VPS with a visible desktop (VNC/RDP) or
   building a live screen-share into the app itself; ask if you want help with either.

9. **Editable submit flow (replaces "watch the browser and submit manually")** — the
   original app was built for local use: it typed the transcript into the platform's
   real text field, then expected *you* to review/edit it directly in the visible
   Chromium window and click Submit yourself before telling the tool to continue. On
   headless cloud hosting there's no visible window, so that step could never complete
   — the "Continue to Next Clip" button existed but had no automated submit behind it.
   The review screen now shows the transcript in an **editable box right in the app** —
   edit it there, then click **"✅ Submit & Continue."** That single click now
   automatically re-types your edited text into the real page, clicks the platform's
   Submit button, and checks whether the next clip loaded — advancing automatically if
   so, or showing "no more tasks" if the queue's empty. You still get full control over
   what's submitted; you just do the editing in the app's text box instead of the
   invisible browser window.

## Setting up automated login

Copy `.env.example` to `.env` locally and fill in your real values, or on Streamlit
Cloud add these under **Advanced settings → Secrets**:
```toml
OPENAI_API_KEY = "sk-..."
INTRON_EMAIL = "your-intron-login-email@example.com"
INTRON_PASSWORD = "your-intron-password"
```
If `INTRON_EMAIL`/`INTRON_PASSWORD` aren't set, the app behaves as before — it'll just
sit waiting for a manual login that can't happen on headless hosting, and time out
after 5 minutes.

## Before you deploy: your OpenAI key

Your `.env` file has a live OpenAI API key in plain text. If this key has been pushed
to GitHub or shared anywhere before, rotate it at platform.openai.com before deploying.
Never commit `.env` — put the key in Streamlit Cloud's Secrets panel instead (see below).

## Step-by-step deployment

### 1. Push this code to GitHub
```bash
cd GlobalAITranscriber
git init
git add .
git status   # confirm .env and browser/sessions/*.json are NOT listed
git commit -m "Prepare for Streamlit Cloud deployment (headless + fixes)"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

If you're pushing to an **existing repo** that previously had `.env` committed, GitHub's
push protection will keep blocking you even after you delete the file, because the key
is still in your commit history. In that case, either:
- Delete the GitHub repo and re-create it, then push this fresh `git init`, or
- Use `git rm --cached .env && git commit --amend` on your very first commit before
  it's ever pushed (doesn't help if it's already been pushed once).

### 2. Create the app on Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
2. **New app** → pick your repo → branch `main` → main file path `app.py`.
3. Before deploying, open **Advanced settings → Secrets** and add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   INTRON_EMAIL = "your-intron-login-email@example.com"
   INTRON_PASSWORD = "your-intron-password"
   ```
   plus any other keys your `.env` currently holds.
4. Click **Deploy**.

### 3. First boot is slower than usual
`playwright install chromium` runs automatically on first load — adds roughly 1–2
minutes once, then it's cached for the container's lifetime.

### 4. Re-authenticating with Intron
Your saved Intron session isn't committed (excluded for security), so the first run on
the cloud will attempt automated login with `INTRON_EMAIL`/`INTRON_PASSWORD` if you set
them (see "Setting up automated login" above). Once that succeeds, the session is saved
and reused for subsequent runs in that container.

## If it still fails after deploying

Check **Manage app → logs** for the exact error. If you see the same
`Executable doesn't exist` error again, it usually means the *old* code got pushed
instead of this fixed copy — check `ui/browser_process.py` line ~106 on GitHub directly
and confirm it says `headless=True`, and that `app.py` contains
`_ensure_playwright_browser_installed`.

## Reverting to local desktop use

To go back to a visible browser window locally, change `headless=True` back to
`headless=False` in both `browser/browser_manager.py` (~line 74) and
`ui/browser_process.py` (~line 106).
