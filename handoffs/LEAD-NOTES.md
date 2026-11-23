# Lead notes (from the integration owner) — read first, updated as needed

## Proven render recipe (verified by lead today)

Vendored engines with node_modules already installed live in the MAIN checkout:
`/Users/darshan/Documents/ChatGPT/imessagevideo-motion-catalog/skill/imessage-motion-recreation/scripts/engines/`
Run engines FROM that directory with absolute --scene/--out paths — no npm ci needed:

```bash
cd /Users/darshan/Documents/ChatGPT/imessagevideo-motion-catalog/skill/imessage-motion-recreation/scripts/engines
CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  node render.mjs --method html --scene /abs/scene.json --out /abs/out.png --frame 30
```

Verified just now: `--method html` produced a real 960x540 PNG (Google Chrome installed at that path; Playwright chromium-1169/1243 also cached at ~/Library/Caches/ms-playwright). If you prefer your own copy, `npm ci` in YOUR worktree's engines dir works too (deps pinned) — but reuse is faster.

ffmpeg/ffprobe 7.1.1, node v23, python3.15 on PATH. Pillow needs its own venv per engines/requirements.txt (create in work/<role>/ if you use Pillow).

## Seed-state correction (catalog agent especially)

`director/motion-catalog/`, the upgraded `cli.mjs` (search/show/scene --motion), `explorer-template.html`, `index.html`, and `handoffs/motion-catalog-previews/` were UNCOMMITTED local work on the user's imv/motion-catalog branch — they do not exist at base commit c49482a. Lead has copied the complete seed state into the catalog worktree. When your commits land on devin-bot they become tracked for the first time — that is intended.

## House rules reminders

- Commit ONLY your owned paths with git add <paths>; never reset/checkout/clean; never commit other agents' files.
- mp4/png exports under work/<role>/ or handoffs/motion-catalog-previews/ are committable deliverables (keep each <24MB).
- Update handoffs/out/<role>/STATUS.md as you go — the observer and other agents read it.
