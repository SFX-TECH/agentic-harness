"""SFX Mission Control v1.2 - one live view of every Claude Code session on this machine.

Zero dependencies (Python 3.10+ stdlib). Reads session transcripts under
~/.claude/projects (each session is a .jsonl the harness writes continuously),
so "active right now" = the file was written seconds ago. Read-only on the
transcripts; the only thing it ever writes is its own config (role labels).

v1.2: the Office view is now a living scene (canvas): every session is an
avatar that walks to its desk, sits and types while the session works, gets
up and wanders when idle, and shows a speech bubble of what it just said.
Board view unchanged. Click any name or avatar to assign a role.

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
  .bar { max-width: 1360px; margin: 0 auto; padding: 16px 28px; display: flex; align-items: center; gap: 16px; }
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
  main { max-width: 1360px; margin: 0 auto; padding: 26px 28px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: 18px; }
  .room { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow);
    overflow: hidden; transition: transform .2s ease; }
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
  #officeWrap { background: var(--surface); border: 1px solid var(--line); border-radius: 16px; box-shadow: var(--shadow); overflow: hidden; }
  #floor { display: block; width: 100%; cursor: default; }
  #menu { position: fixed; z-index: 60; background: var(--surface); border: 1px solid var(--line); border-radius: 12px;
    box-shadow: 0 12px 40px -8px rgba(20,24,31,.25); min-width: 210px; padding: 6px; display: none; }
  #menu .mi { display: block; width: 100%; text-align: left; border: 0; background: transparent; font: inherit;
    font-size: 13.5px; padding: 8px 11px; border-radius: 8px; cursor: pointer; color: var(--ink); }
  #menu .mi:hover { background: #F1F6F4; color: var(--teal-deep); }
  #menu .mi.muted { color: var(--ink-3); }
  #menu input { width: 100%; border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; font: inherit; font-size: 13.5px; margin: 4px 0 2px; }
  #menu input:focus { outline: 2px solid var(--teal); border-color: transparent; }
  .empty { padding: 80px 20px; text-align: center; color: var(--ink-3); }
  footer { max-width: 1360px; margin: 0 auto; padding: 8px 28px 32px; font-size: 12px; color: var(--ink-3); }
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
<footer>Click any session name or avatar to assign a role (saved to <code>mission_control.config.json</code>). Read-only on transcripts. Data refreshes every 4s.</footer>
<script>
const esc = s => s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ago = s => s < 8 ? 'now' : s < 120 ? Math.round(s) + 's' : s < 7200 ? Math.round(s/60) + 'm' : s < 172800 ? Math.round(s/3600) + 'h' : Math.round(s/86400) + 'd';
const HUES = ['#0FA588','#5B7DB1','#B1745B','#8B6BB1','#4E9C6C','#C2A23C'];
const hue = sid => HUES[parseInt(sid.slice(0,4),16) % HUES.length];
const REDUCED = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
let view = localStorage.getItem('mc.view') || 'board';
let lastData = null;

/* ================= Board view (unchanged) ================= */
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

/* ================= Office view: the living scene ================= */
const scene = { zones: [], avatars: new Map(), hits: [], canvas: null, ctx: null, w: 0, h: 0, raf: 0 };

function layoutZones(d, W) {
  const zones = []; let x = 16, y = 16, rowH = 0;
  for (const p of d.projects) {
    const n = p.sessions.length;
    const w = Math.max(240, 56 + n * 118), h = 224;
    if (x + w > W - 16 && x > 16) { x = 16; y += rowH + 16; rowH = 0; }
    const desks = p.sessions.map((s, i) => ({ s, slug: p.slug, x: x + 46 + i * 118, y: y + 78 }));
    zones.push({ p, x, y, w, h, desks });
    x += w + 16; rowH = Math.max(rowH, h);
  }
  return { zones, height: Math.max(y + rowH + 16, 300) };
}

function syncAvatars() {
  const seen = new Set();
  for (const z of scene.zones) for (const dsk of z.desks) {
    const s = dsk.s; seen.add(s.id);
    let a = scene.avatars.get(s.id);
    const chair = { x: dsk.x + 35, y: dsk.y + 34 };
    if (!a) {
      a = { sid: s.id, color: hue(s.id), x: chair.x + (Math.random()*120-60), y: chair.y + 40,
            tx: chair.x, ty: chair.y, mode: 'walk', phase: Math.random()*6, wait: 0,
            bubble: '', bubbleT: 0, lastSnip: s.snippet || '' };
      scene.avatars.set(s.id, a);
    }
    a.desk = dsk; a.zone = z; a.state = s.state; a.label = s.label; a.chair = chair;
    if (s.snippet && s.snippet !== a.lastSnip) {
      a.lastSnip = s.snippet;
      if (s.state === 'active') { a.bubble = s.snippet.slice(0, 64); a.bubbleT = 7; }
    }
  }
  for (const k of [...scene.avatars.keys()]) if (!seen.has(k)) scene.avatars.delete(k);
}

function wanderTarget(a) {
  const z = a.zone;
  return { x: z.x + 30 + Math.random() * (z.w - 60), y: z.y + 150 + Math.random() * (z.h - 185) };
}

function stepAvatar(a, dt) {
  a.phase += dt * (a.mode === 'walk' ? 9 : 2.2);
  if (a.bubbleT > 0) a.bubbleT -= dt;
  const speed = 55;
  if (a.state === 'active') {
    // go sit and type
    if (a.mode !== 'sit') { a.tx = a.chair.x; a.ty = a.chair.y; a.mode = 'walk'; }
  } else if (a.state === 'idle') {
    if (a.mode === 'sit') { a.mode = 'walk'; const t = wanderTarget(a); a.tx = t.x; a.ty = t.y; }
    if (a.mode === 'stand') { a.wait -= dt; if (a.wait <= 0) { const t = wanderTarget(a); a.tx = t.x; a.ty = t.y; a.mode = 'walk'; } }
  }
  if (a.mode === 'walk') {
    const dx = a.tx - a.x, dy = a.ty - a.y, dist = Math.hypot(dx, dy);
    if (dist < 3) {
      if (a.state === 'active' && Math.abs(a.tx - a.chair.x) < 4 && Math.abs(a.ty - a.chair.y) < 4) { a.mode = 'sit'; }
      else { a.mode = 'stand'; a.wait = 3 + Math.random() * 6; }
    } else {
      a.x += dx / dist * speed * dt; a.y += dy / dist * speed * dt; a.face = dx >= 0 ? 1 : -1;
    }
  }
}

function rr(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }

function drawDesk(ctx, dsk) {
  const { x, y, s } = dsk;
  // monitor
  const scr = s.state === 'active' ? '#00D4AA' : s.state === 'idle' ? '#EFCB84' : '#DDE1E6';
  if (s.state === 'active') { ctx.save(); ctx.shadowColor = 'rgba(0,212,170,.55)'; ctx.shadowBlur = 10; }
  ctx.fillStyle = scr; rr(ctx, x + 12, y - 26, 46, 28, 5); ctx.fill();
  if (s.state === 'active') ctx.restore();
  ctx.fillStyle = '#C9CFD6'; ctx.fillRect(x + 31, y + 2, 8, 6);
  // table + legs
  ctx.fillStyle = '#E2DED6'; rr(ctx, x, y + 8, 70, 9, 3); ctx.fill();
  ctx.fillStyle = '#D8D3C8'; ctx.fillRect(x + 4, y + 17, 5, 20); ctx.fillRect(x + 61, y + 17, 5, 20);
}

function drawAvatar(ctx, a, t) {
  const sitting = a.mode === 'sit';
  const walking = a.mode === 'walk';
  const bobY = sitting && !REDUCED ? Math.sin(a.phase) * 1.3 : 0;
  const x = a.x, y = a.y + bobY;
  // shadow
  ctx.fillStyle = 'rgba(20,24,31,.10)';
  ctx.beginPath(); ctx.ellipse(a.x, a.y + 20, 12, 4, 0, 0, 7); ctx.fill();
  // legs (walking only)
  if (walking && !REDUCED) {
    const sw = Math.sin(a.phase) * 5;
    ctx.strokeStyle = a.color; ctx.lineWidth = 3.4; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x - 3, y + 8); ctx.lineTo(x - 3 + sw, y + 19); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x + 3, y + 8); ctx.lineTo(x + 3 - sw, y + 19); ctx.stroke();
  }
  // body
  ctx.fillStyle = a.color; ctx.globalAlpha = 0.85;
  rr(ctx, x - 9, y - 6, 18, sitting ? 15 : 17, 8); ctx.fill();
  ctx.globalAlpha = 1;
  // typing hands
  if (sitting && !REDUCED) {
    const tap = Math.sin(a.phase * 2.6) * 1.6;
    ctx.fillStyle = a.color;
    ctx.beginPath(); ctx.arc(x - 6, y + 2 + tap, 2.2, 0, 7); ctx.fill();
    ctx.beginPath(); ctx.arc(x + 6, y + 2 - tap, 2.2, 0, 7); ctx.fill();
  }
  // head
  ctx.fillStyle = a.color;
  ctx.beginPath(); ctx.arc(x, y - 13, 8, 0, 7); ctx.fill();
  ctx.fillStyle = 'rgba(255,255,255,.28)';
  ctx.beginPath(); ctx.arc(x - 2.5, y - 15.5, 2.6, 0, 7); ctx.fill();
  // name tag
  const tag = a.label || a.sid;
  ctx.font = '600 10.5px "Outfit","Segoe UI",sans-serif';
  ctx.textAlign = 'center'; ctx.fillStyle = '#5A6472';
  ctx.fillText(tag.length > 20 ? tag.slice(0, 19) + '…' : tag, x, y + 32);
  // speech bubble
  if (a.bubbleT > 0 && a.bubble) {
    const alpha = Math.min(1, a.bubbleT);
    ctx.globalAlpha = alpha;
    ctx.font = '500 11px "Outfit","Segoe UI",sans-serif';
    const txt = a.bubble.length > 40 ? a.bubble.slice(0, 39) + '…' : a.bubble;
    const w = ctx.measureText(txt).width + 18;
    const bx = Math.max(8, Math.min(x - w / 2, scene.w - w - 8)), by = y - 52;
    ctx.fillStyle = '#FFFFFF'; ctx.strokeStyle = '#E8E6E1'; ctx.lineWidth = 1;
    rr(ctx, bx, by, w, 22, 11); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - 4, by + 22); ctx.lineTo(x + 4, by + 22); ctx.lineTo(x, by + 28); ctx.closePath();
    ctx.fillStyle = '#FFFFFF'; ctx.fill(); ctx.strokeStyle = '#E8E6E1';
    ctx.beginPath(); ctx.moveTo(x - 4, by + 22); ctx.lineTo(x, by + 28); ctx.lineTo(x + 4, by + 22); ctx.stroke();
    ctx.fillStyle = '#14181F'; ctx.textAlign = 'left';
    ctx.fillText(txt, bx + 9, by + 15);
    ctx.globalAlpha = 1;
  }
}

let lastT = 0;
function frame(t) {
  scene.raf = requestAnimationFrame(frame);
  const dt = Math.min(0.06, (t - lastT) / 1000 || 0.016); lastT = t;
  const ctx = scene.ctx; if (!ctx || !lastData) return;
  ctx.clearRect(0, 0, scene.w, scene.h);
  // floor
  ctx.fillStyle = '#F5F3EE'; ctx.fillRect(0, 0, scene.w, scene.h);
  ctx.strokeStyle = 'rgba(20,24,31,.03)'; ctx.lineWidth = 1;
  for (let gx = 0; gx < scene.w; gx += 26) { ctx.beginPath(); ctx.moveTo(gx, 0); ctx.lineTo(gx, scene.h); ctx.stroke(); }
  for (let gy = 0; gy < scene.h; gy += 26) { ctx.beginPath(); ctx.moveTo(0, gy); ctx.lineTo(scene.w, gy); ctx.stroke(); }
  scene.hits = [];
  // zones
  for (const z of scene.zones) {
    const live = z.p.sessions.some(s => s.state === 'active');
    ctx.fillStyle = '#FFFFFF'; ctx.strokeStyle = live ? '#00D4AA' : '#E8E6E1'; ctx.lineWidth = live ? 2 : 1;
    rr(ctx, z.x, z.y, z.w, z.h, 14); ctx.fill(); ctx.stroke();
    ctx.font = '700 13.5px "Outfit","Segoe UI",sans-serif'; ctx.textAlign = 'left';
    ctx.fillStyle = '#14181F';
    let nm = z.p.name; const maxW = z.w - 100;
    if (ctx.measureText(nm).width > maxW) {
      while (nm.length > 4 && ctx.measureText(nm + '…').width > maxW) nm = nm.slice(0, -1);
      nm = nm.trimEnd() + '…';
    }
    ctx.fillText(nm, z.x + 16, z.y + 24);
    ctx.font = '600 11px "Outfit","Segoe UI",sans-serif'; ctx.textAlign = 'right';
    ctx.fillStyle = '#98A1AD'; ctx.fillText(ago(z.p.newest_age) + ' ago', z.x + z.w - 14, z.y + 24);
    ctx.textAlign = 'left';
    for (const dsk of z.desks) {
      drawDesk(ctx, dsk);
      scene.hits.push({ x: dsk.x - 6, y: dsk.y - 30, w: 84, h: 92, sid: dsk.s.id, slug: dsk.slug });
    }
  }
  // avatars (skip asleep sessions: empty desk tells the story)
  for (const a of scene.avatars.values()) {
    if (a.state === 'asleep') continue;
    if (!REDUCED) stepAvatar(a, dt);
    else { a.x = a.chair.x; a.y = a.chair.y; a.mode = a.state === 'active' ? 'sit' : 'stand'; }
    drawAvatar(ctx, a);
  }
}

function renderOffice() {
  const root = document.getElementById('root');
  root.innerHTML = '<div id="officeWrap"><canvas id="floor"></canvas></div>';
  scene.canvas = document.getElementById('floor');
  scene.ctx = scene.canvas.getContext('2d');
  relayout();
  scene.canvas.addEventListener('click', e => {
    const r = scene.canvas.getBoundingClientRect();
    const cx = e.clientX - r.left, cy = e.clientY - r.top;
    const hit = scene.hits.find(h => cx >= h.x && cx <= h.x + h.w && cy >= h.y && cy <= h.y + h.h);
    if (hit) openMenu(e.clientX, e.clientY, hit.sid, hit.slug); else closeMenu();
  });
  scene.canvas.addEventListener('mousemove', e => {
    const r = scene.canvas.getBoundingClientRect();
    const cx = e.clientX - r.left, cy = e.clientY - r.top;
    scene.canvas.style.cursor = scene.hits.some(h => cx >= h.x && cx <= h.x + h.w && cy >= h.y && cy <= h.y + h.h) ? 'pointer' : 'default';
  });
  cancelAnimationFrame(scene.raf);
  lastT = 0;
  scene.raf = requestAnimationFrame(frame);
}

function relayout() {
  if (!scene.canvas || !lastData) return;
  const cssW = scene.canvas.parentElement.clientWidth;
  const L = layoutZones(lastData, cssW);
  scene.zones = L.zones; scene.w = cssW; scene.h = L.height;
  const dpr = window.devicePixelRatio || 1;
  scene.canvas.width = cssW * dpr; scene.canvas.height = L.height * dpr;
  scene.canvas.style.height = L.height + 'px';
  scene.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  syncAvatars();
}

window.addEventListener('resize', () => { if (view === 'office') relayout(); });

/* ================= shared ================= */
function render() {
  if (!lastData) return;
  const d = lastData;
  document.getElementById('chips').innerHTML =
    `<span class="chip"><span class="dot active"></span><b>${d.totals.active}</b>&nbsp;working</span>` +
    `<span class="chip"><span class="dot idle"></span><b>${d.totals.idle}</b>&nbsp;idle</span>` +
    `<span class="chip"><b>${d.totals.sessions}</b>&nbsp;sessions · <b>${d.totals.projects}</b>&nbsp;projects</span>`;
  document.getElementById('vBoard').className = view === 'board' ? 'on' : '';
  document.getElementById('vOffice').className = view === 'office' ? 'on' : '';
  if (!d.projects.length) { document.getElementById('root').innerHTML = '<div class="empty">No recent sessions.</div>'; return; }
  if (view === 'board') { cancelAnimationFrame(scene.raf); scene.canvas = null; document.getElementById('root').innerHTML = renderBoard(d); }
  else if (!scene.canvas) renderOffice();
  else relayout();
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
  const r = await fetch('/data', {cache: 'no-store'}); lastData = await r.json();
  if (view === 'board') render(); else { relayout(); }
}
function openMenu(px, py, sid, slug) {
  const proj = (lastData.projects || []).find(p => p.slug === slug) || {roles: []};
  menu.innerHTML = proj.roles.map(rr2 => `<button class="mi" data-v="${esc(rr2)}">${esc(rr2)}</button>`).join('') +
    `<button class="mi" data-custom="1">Custom…</button>` +
    `<button class="mi muted" data-v="">Clear label</button>`;
  menu.style.display = 'block';
  menu.style.left = Math.min(px, window.innerWidth - 240) + 'px';
  menu.style.top = Math.min(py + 8, window.innerHeight - 200) + 'px';
  menu.querySelectorAll('.mi').forEach(mi => mi.onclick = () => {
    if (mi.dataset.custom) {
      menu.innerHTML = `<input id="ci" placeholder="Role name" maxlength="48">`;
      const ci = document.getElementById('ci');
      ci.focus();
      ci.onkeydown = ev => { if (ev.key === 'Enter') setLabel(sid, ci.value); if (ev.key === 'Escape') closeMenu(); };
    } else setLabel(sid, mi.dataset.v);
  });
}
document.addEventListener('click', e => {
  const btn = e.target.closest('.who');
  if (btn) { const r = btn.getBoundingClientRect(); openMenu(r.left, r.bottom, btn.dataset.sid, btn.dataset.slug); return; }
  if (!e.target.closest('#menu') && e.target.id !== 'floor') closeMenu();
});
document.getElementById('vBoard').onclick = () => { view = 'board'; localStorage.setItem('mc.view', view); render(); };
document.getElementById('vOffice').onclick = () => { view = 'office'; localStorage.setItem('mc.view', view); scene.canvas = null; render(); };
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
    print(f"SFX Mission Control v1.2 -> http://localhost:{PORT}")
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
