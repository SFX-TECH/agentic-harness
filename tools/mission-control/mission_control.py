"""SFX Mission Control v1.1 - one live view of every Claude Code session on this machine.

Zero dependencies (Python 3.10+ stdlib). Reads session transcripts under
~/.claude/projects (each session is a .jsonl the harness writes continuously),
so "active right now" = the file was written seconds ago. Read-only on the
transcripts; the only thing it ever writes is its own config (role labels).

v1.1: per-project role vocab + click-to-label in the UI (POST /label persists
to config, survives restarts), plus the Office view - an ambient scene where
every session is a figure at a desk, typing when active.

Run:    python mission_control.py          (serves http://localhost:3131)
Config: mission_control.config.json (auto-created; edits apply live)
"""
from __future__ import annotations

import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

PORT = 3131
PROJECTS_DIR = Path.home() / ".claude" / "projects"
CONFIG_PATH = Path(__file__).with_name("mission_control.config.json")
RETENTION_DAYS = 14
MAX_SESSIONS_PER_PROJECT = 6
SNIPPET_TAIL_BYTES = 262_144

ACTIVE_S = 150
IDLE_S = 3_600

DEFAULT_CONFIG = {
    "_help": "names: project slug -> display name. labels: sid8 -> role. roles: project slug -> role vocab shown in the click-to-label menu. hide: slugs.",
    "names": {},
    "labels": {},
    "roles": {
        "_default": ["Worker", "Advisor", "Research"],
    },
    "hide": [],
}

_snippet_cache: dict[str, tuple[float, str]] = {}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    try:
        cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return dict(DEFAULT_CONFIG)
    for key, val in DEFAULT_CONFIG.items():
        cfg.setdefault(key, val if not isinstance(val, dict) else dict(val))
    return cfg


def save_label(sid8: str, label: str) -> bool:
    if not re.fullmatch(r"[0-9a-f]{8}", sid8):
        return False
    label = label.strip()[:48]
    cfg = load_config()
    labels = cfg.setdefault("labels", {})
    if label:
        labels[sid8] = label
    else:
        labels.pop(sid8, None)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return True


def clean_slug(slug: str) -> str:
    s = re.sub(r"^([A-Za-z])--", r"\1: ", slug)
    return s.replace("-", " ").strip()


def last_assistant_text(path: Path, mtime: float) -> str:
    key = str(path)
    hit = _snippet_cache.get(key)
    if hit and hit[0] == mtime:
        return hit[1]
    text = ""
    try:
        size = path.stat().st_size
        with open(path, "rb") as f:
            if size > SNIPPET_TAIL_BYTES:
                f.seek(size - SNIPPET_TAIL_BYTES)
                f.readline()
            lines = f.read().decode("utf-8", errors="replace").splitlines()
        for line in reversed(lines):
            if '"assistant"' not in line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                continue
            if obj.get("type") != "assistant":
                continue
            content = (obj.get("message") or {}).get("content")
            if isinstance(content, str):
                candidate = content
            elif isinstance(content, list):
                candidate = next(
                    (b.get("text", "") for b in content
                     if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip()),
                    "",
                )
            else:
                candidate = ""
            candidate = re.sub(r"\s+", " ", candidate).strip()
            candidate = re.sub(r"[#*`>|]", "", candidate).strip()
            if candidate:
                text = candidate[:170]
                break
    except Exception:
        text = ""
    _snippet_cache[key] = (mtime, text)
    return text


def scan() -> dict:
    cfg = load_config()
    names = cfg.get("names", {})
    labels = cfg.get("labels", {})
    roles_cfg = cfg.get("roles", {})
    hidden = set(cfg.get("hide", []))
    now = time.time()
    projects = []
    if PROJECTS_DIR.is_dir():
        for d in PROJECTS_DIR.iterdir():
            if not d.is_dir() or d.name in hidden:
                continue
            sessions = []
            for f in d.glob("*.jsonl"):
                try:
                    st = f.stat()
                except OSError:
                    continue
                age = now - st.st_mtime
                if age > RETENTION_DAYS * 86_400 or st.st_size < 2_000:
                    continue
                sid = f.stem
                state = "active" if age < ACTIVE_S else ("idle" if age < IDLE_S else "asleep")
                sessions.append({
                    "id": sid[:8],
                    "label": labels.get(sid[:8], ""),
                    "age_s": int(age),
                    "state": state,
                    "size_kb": st.st_size // 1024,
                    "snippet": last_assistant_text(f, st.st_mtime) if age < 86_400 else "",
                })
            if not sessions:
                continue
            sessions.sort(key=lambda s: s["age_s"])
            sessions = sessions[:MAX_SESSIONS_PER_PROJECT]
            projects.append({
                "slug": d.name,
                "name": names.get(d.name, clean_slug(d.name)),
                "roles": roles_cfg.get(d.name, roles_cfg.get("_default", [])),
                "newest_age": sessions[0]["age_s"],
                "sessions": sessions,
            })
    projects.sort(key=lambda p: p["newest_age"])
    totals = {
        "projects": len(projects),
        "active": sum(1 for p in projects for s in p["sessions"] if s["state"] == "active"),
        "idle": sum(1 for p in projects for s in p["sessions"] if s["state"] == "idle"),
        "sessions": sum(len(p["sessions"]) for p in projects),
    }
    return {"generated": int(now), "totals": totals, "projects": projects}


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SFX Mission Control</title>
<style>
  :root {
    --bg: #F7F7F4; --surface: #FFFFFF; --line: #E8E6E1; --floor: #F2F0EA;
    --ink: #14181F; --ink-2: #5A6472; --ink-3: #98A1AD;
    --teal: #00D4AA; --teal-deep: #087F66;
    --shadow: 0 1px 2px rgba(20,24,31,.05), 0 8px 24px -12px rgba(20,24,31,.12);
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  html { -webkit-font-smoothing: antialiased; }
  body { background: var(--bg); color: var(--ink); min-height: 100vh;
    font-family: "Outfit", "Syne", "Segoe UI Variable Text", "Segoe UI", system-ui, sans-serif;
    font-size: 15px; line-height: 1.55; }
  header { position: sticky; top: 0; z-index: 30; background: rgba(247,247,244,.88);
    backdrop-filter: blur(12px); border-bottom: 1px solid var(--line); }
  .bar { max-width: 1320px; margin: 0 auto; padding: 16px 28px; display: flex; align-items: center; gap: 16px; }
  .mark { display: flex; align-items: center; gap: 11px; }
  .mark h1 { font-size: 17px; font-weight: 700; letter-spacing: -0.01em; }
  .mark h1 span { color: var(--ink-3); font-weight: 500; }
  .seg { display: inline-flex; background: #EFEDE8; border: 1px solid var(--line); border-radius: 10px; padding: 3px; margin-left: 18px; }
  .seg button { border: 0; background: transparent; padding: 6px 14px; border-radius: 8px; font: inherit;
    font-size: 13px; font-weight: 650; color: var(--ink-2); cursor: pointer; transition: background .18s, color .18s; }
  .seg button:focus-visible { outline: 2px solid var(--teal-deep); outline-offset: 1px; }
  .seg button.on { background: var(--surface); color: var(--ink); box-shadow: 0 1px 2px rgba(20,24,31,.08); }
  .chips { margin-left: auto; display: flex; gap: 8px; align-items: center; }
  .chip { display: inline-flex; align-items: center; gap: 7px; padding: 6px 13px; background: var(--surface);
    border: 1px solid var(--line); border-radius: 999px; font-size: 12.5px; font-weight: 600; color: var(--ink-2);
    font-variant-numeric: tabular-nums; }
  .chip b { color: var(--ink); font-weight: 700; }
  .dot { width: 8px; height: 8px; border-radius: 50%; flex: none; }
  .dot.active { background: var(--teal); animation: pulse 2s infinite; }
  .dot.idle { background: #E3A83B; }
  .dot.asleep { background: #C9CFD6; }
  @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0,212,170,.45);} 70% { box-shadow: 0 0 0 9px rgba(0,212,170,0);} 100% { box-shadow: 0 0 0 0 rgba(0,212,170,0);} }
  main { max-width: 1320px; margin: 0 auto; padding: 26px 28px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; }
  .room { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow);
    overflow: hidden; transition: transform .2s ease, box-shadow .2s ease; }
  .room:hover { transform: translateY(-1px); }
  .room.live { border-top: 3px solid var(--teal); }
  .room-h { padding: 15px 20px 9px; display: flex; align-items: baseline; gap: 10px; }
  .room-h h2 { font-size: 15.5px; font-weight: 700; letter-spacing: -0.01em; }
  .room-h .when { margin-left: auto; font-size: 12px; color: var(--ink-3); font-variant-numeric: tabular-nums; white-space: nowrap; }
  .sess { border-top: 1px solid #F1EFEA; padding: 11px 20px 12px; }
  .sess-top { display: flex; align-items: center; gap: 9px; }
  .who { font-size: 13.5px; font-weight: 650; color: var(--ink); background: transparent; border: 0; padding: 2px 4px;
    margin: -2px -4px; border-radius: 6px; cursor: pointer; font-family: inherit; }
  .who:hover { background: #EFF7F4; color: var(--teal-deep); }
  .who:focus-visible { outline: 2px solid var(--teal-deep); }
  .sid { font-size: 11.5px; color: var(--ink-3); font-family: "IBM Plex Mono", Consolas, monospace; }
  .ago { margin-left: auto; font-size: 12px; font-weight: 600; font-variant-numeric: tabular-nums; color: var(--ink-3); }
  .ago.active { color: var(--teal-deep); }
  .snippet { margin-top: 5px; font-size: 12.8px; color: var(--ink-2); line-height: 1.5;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
  /* ---------- Office view ---------- */
  .office { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px; }
  .oroom { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); overflow: hidden; }
  .oroom.live { border-top: 3px solid var(--teal); }
  .oroom-h { padding: 13px 18px 8px; display: flex; align-items: baseline; }
  .oroom-h h2 { font-size: 14.5px; font-weight: 700; }
  .oroom-h .when { margin-left: auto; font-size: 11.5px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  .ofloor { background: var(--floor); border-top: 1px solid #ECE9E2; padding: 16px 12px 10px; display: flex; flex-wrap: wrap;
    gap: 4px 2px; justify-content: center; min-height: 128px;
    background-image: linear-gradient(rgba(20,24,31,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(20,24,31,.025) 1px, transparent 1px);
    background-size: 24px 24px; }
  .desk { width: 104px; text-align: center; }
  .desk button.tag { border: 0; background: transparent; font: inherit; font-size: 11.5px; font-weight: 650; color: var(--ink);
    cursor: pointer; padding: 1px 6px; border-radius: 6px; max-width: 104px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .desk button.tag:hover { background: #EAF5F1; color: var(--teal-deep); }
  .desk .dago { font-size: 10.5px; color: var(--ink-3); font-variant-numeric: tabular-nums; }
  .figure { transform-origin: 48px 62px; }
  .desk.active .figure { animation: bob 1.5s ease-in-out infinite; }
  @keyframes bob { 0%,100% { transform: translateY(0); } 50% { transform: translateY(1.6px); } }
  .desk.active .screen { fill: var(--teal); filter: drop-shadow(0 0 5px rgba(0,212,170,.55)); }
  .desk.idle .screen { fill: #EFCB84; }
  .desk.asleep .screen { fill: #DDE1E6; }
  .desk.asleep svg { opacity: .5; }
  .desk .keys { opacity: 0; }
  .desk.active .keys { opacity: 1; animation: keys 0.9s steps(2) infinite; }
  @keyframes keys { 0%,100% { transform: translateX(0);} 50% { transform: translateX(1.5px);} }
  @media (prefers-reduced-motion: reduce) {
    .dot.active { animation: none; }
    .desk.active .figure, .desk.active .keys { animation: none; }
  }
  /* label menu */
  #menu { position: fixed; z-index: 60; background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
    box-shadow: 0 12px 40px -8px rgba(20,24,31,.25); min-width: 210px; padding: 6px; display: none; }
  #menu .mi { display: block; width: 100%; text-align: left; border: 0; background: transparent; font: inherit;
    font-size: 13.5px; padding: 8px 11px; border-radius: 8px; cursor: pointer; color: var(--ink); }
  #menu .mi:hover { background: #F1F6F4; color: var(--teal-deep); }
  #menu .mi.muted { color: var(--ink-3); }
  #menu input { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; font: inherit; font-size: 13.5px; margin: 4px 0 2px; }
  #menu input:focus { outline: 2px solid var(--teal); border-color: transparent; }
  .empty { padding: 80px 20px; text-align: center; color: var(--ink-3); }
  footer { max-width: 1320px; margin: 0 auto; padding: 8px 28px 32px; font-size: 12px; color: var(--ink-3); }
  footer code { font-family: "IBM Plex Mono", Consolas, monospace; font-size: 11.5px; }
</style>
</head>
<body>
<header><div class="bar">
  <div class="mark">
    <svg width="26" height="26" viewBox="0 0 26 26" aria-hidden="true">
      <rect x="1" y="1" width="24" height="24" rx="7" fill="#14181F"/>
      <circle cx="13" cy="13" r="4.6" fill="#00D4AA"/>
    </svg>
    <h1>Mission Control <span>/ SFX Tech</span></h1>
  </div>
  <div class="seg" role="tablist" aria-label="View">
    <button id="vBoard" role="tab">Board</button>
    <button id="vOffice" role="tab">Office</button>
  </div>
  <div class="chips" id="chips" aria-live="polite"></div>
</div></header>
<main><div id="root"><div class="empty">Connecting…</div></div></main>
<div id="menu" role="menu"></div>
<footer>Click any session name to assign a role (saved to <code>mission_control.config.json</code>). Read-only on transcripts. Refreshes every 4s.</footer>
<script>
const esc = s => s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ago = s => s < 8 ? 'now' : s < 120 ? Math.round(s) + 's' : s < 7200 ? Math.round(s/60) + 'm' : s < 172800 ? Math.round(s/3600) + 'h' : Math.round(s/86400) + 'd';
const HUES = ['#0FA588','#5B7DB1','#B1745B','#8B6BB1','#4E9C6C','#C2A23C'];
const hue = sid => HUES[parseInt(sid.slice(0,4),16) % HUES.length];
let view = localStorage.getItem('mc.view') || 'board';
let lastData = null;

function deskSVG(sid) {
  const c = hue(sid);
  return `<svg viewBox="0 0 96 88" width="96" height="88" aria-hidden="true">
    <rect x="27" y="8" width="42" height="27" rx="4" class="screen" fill="#DDE1E6"/>
    <rect x="44" y="35" width="8" height="6" fill="#C9CFD6"/>
    <rect x="13" y="41" width="70" height="8" rx="3" fill="#E2DED6"/>
    <rect x="17" y="49" width="6" height="20" fill="#D8D3C8"/>
    <rect x="73" y="49" width="6" height="20" fill="#D8D3C8"/>
    <rect x="38" y="44" width="20" height="3" rx="1.5" class="keys" fill="#B9C0C9"/>
    <g class="figure">
      <circle cx="48" cy="60" r="9.5" fill="${c}"/>
      <rect x="34" y="70" width="28" height="15" rx="7.5" fill="${c}" opacity="0.82"/>
    </g>
  </svg>`;
}

function renderBoard(d) {
  return '<div class="grid">' + d.projects.map(p => {
    const live = p.sessions.some(s => s.state === 'active');
    return `<section class="room${live ? ' live' : ''}">
      <div class="room-h"><h2>${esc(p.name)}</h2><span class="when">${ago(p.newest_age)} ago</span></div>
      ${p.sessions.map(s => `
        <div class="sess">
          <div class="sess-top">
            <span class="dot ${s.state}"></span>
            <button class="who" data-sid="${s.id}" data-slug="${esc(p.slug)}" title="Assign role">${esc(s.label || 'Session')}</button>
            <span class="sid">${s.id}</span>
            <span class="ago ${s.state}">${s.state === 'active' ? 'working · ' : ''}${ago(s.age_s)}</span>
          </div>
          ${s.snippet ? `<div class="snippet">${esc(s.snippet)}</div>` : ''}
        </div>`).join('')}
    </section>`;
  }).join('') + '</div>';
}

function renderOffice(d) {
  return '<div class="office">' + d.projects.map(p => {
    const live = p.sessions.some(s => s.state === 'active');
    return `<section class="oroom${live ? ' live' : ''}">
      <div class="oroom-h"><h2>${esc(p.name)}</h2><span class="when">${ago(p.newest_age)} ago</span></div>
      <div class="ofloor">
        ${p.sessions.map(s => `
          <div class="desk ${s.state}" title="${esc(s.snippet || s.id)}">
            ${deskSVG(s.id)}
            <button class="tag who" data-sid="${s.id}" data-slug="${esc(p.slug)}" title="Assign role">${esc(s.label || s.id)}</button>
            <div class="dago">${s.state === 'active' ? 'typing' : ago(s.age_s)}</div>
          </div>`).join('')}
      </div>
    </section>`;
  }).join('') + '</div>';
}

function render() {
  if (!lastData) return;
  const d = lastData;
  document.getElementById('chips').innerHTML =
    `<span class="chip"><span class="dot active"></span><b>${d.totals.active}</b>&nbsp;working</span>` +
    `<span class="chip"><span class="dot idle"></span><b>${d.totals.idle}</b>&nbsp;idle</span>` +
    `<span class="chip"><b>${d.totals.sessions}</b>&nbsp;sessions · <b>${d.totals.projects}</b>&nbsp;projects</span>`;
  document.getElementById('vBoard').className = view === 'board' ? 'on' : '';
  document.getElementById('vOffice').className = view === 'office' ? 'on' : '';
  const root = document.getElementById('root');
  root.innerHTML = d.projects.length ? (view === 'board' ? renderBoard(d) : renderOffice(d)) : '<div class="empty">No recent sessions.</div>';
}

async function tick() {
  try {
    const r = await fetch('/data', {cache: 'no-store'});
    lastData = await r.json();
    if (document.getElementById('menu').style.display !== 'block') render();
  } catch (e) {}
}

/* ---- label menu ---- */
const menu = document.getElementById('menu');
function closeMenu() { menu.style.display = 'none'; }
async function setLabel(sid, label) {
  closeMenu();
  await fetch('/label', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({sid, label})});
  await tick(); render();
}
document.addEventListener('click', e => {
  const btn = e.target.closest('.who');
  if (!btn) { if (!e.target.closest('#menu')) closeMenu(); return; }
  const sid = btn.dataset.sid, slug = btn.dataset.slug;
  const proj = (lastData.projects || []).find(p => p.slug === slug) || {roles: []};
  menu.innerHTML = proj.roles.map(rr => `<button class="mi" data-v="${esc(rr)}">${esc(rr)}</button>`).join('') +
    `<button class="mi" data-custom="1">Custom…</button>` +
    `<button class="mi muted" data-v="">Clear label</button>`;
  menu.style.display = 'block';
  const r = btn.getBoundingClientRect();
  menu.style.left = Math.min(r.left, window.innerWidth - 240) + 'px';
  menu.style.top = (r.bottom + 6) + 'px';
  menu.querySelectorAll('.mi').forEach(mi => mi.onclick = () => {
    if (mi.dataset.custom) {
      menu.innerHTML = `<input id="ci" placeholder="Role name" maxlength="48">`;
      const ci = document.getElementById('ci');
      ci.focus();
      ci.onkeydown = ev => { if (ev.key === 'Enter') setLabel(sid, ci.value); if (ev.key === 'Escape') closeMenu(); };
    } else setLabel(sid, mi.dataset.v);
  });
});
document.getElementById('vBoard').onclick = () => { view = 'board'; localStorage.setItem('mc.view', view); render(); };
document.getElementById('vOffice').onclick = () => { view = 'office'; localStorage.setItem('mc.view', view); render(); };
tick(); setInterval(tick, 4000);
</script>
</body>
</html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/data"):
            self._send(json.dumps(scan()).encode("utf-8"), "application/json")
        elif self.path == "/" or self.path.startswith("/index"):
            self._send(PAGE.encode("utf-8"), "text/html; charset=utf-8")
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        if self.path != "/label":
            self.send_response(404); self.end_headers(); return
        try:
            n = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(n).decode("utf-8"))
            ok = save_label(str(payload.get("sid", "")), str(payload.get("label", "")))
        except Exception:
            ok = False
        self._send(json.dumps({"ok": ok}).encode("utf-8"), "application/json", 200 if ok else 400)

    def log_message(self, *_):
        pass


if __name__ == "__main__":
    load_config()
    print(f"SFX Mission Control v1.1 -> http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
