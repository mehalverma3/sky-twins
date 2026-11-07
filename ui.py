import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;700&family=Inter:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
h1, h2, h3, h4 { font-family: 'Cormorant Garamond', Georgia, serif !important; letter-spacing: .02em; }
.sky-badge { display:inline-block; padding:2px 10px; border-radius:999px; font-size:.72rem;
  letter-spacing:.08em; text-transform:uppercase; border:1px solid rgba(232,184,75,.45);
  color:#E8B84B; background:rgba(232,184,75,.08); }
.sky-card { background:#1A1722; border:1px solid rgba(255,255,255,.07);
  border-radius:14px; padding:14px 18px; margin:12px 0; }
.sky-row { display:flex; justify-content:space-between; align-items:center;
  padding:9px 2px; border-bottom:1px solid rgba(255,255,255,.06); gap:12px; }
.sky-row:last-child { border-bottom:none; }
.sky-muted { color:#9A93AB; font-size:.85rem; }
.sky-score { color:#E8B84B; font-weight:600; font-size:.85rem; white-space:nowrap; }
.sky-date { font-family:'Cormorant Garamond', Georgia, serif; font-size:1.4rem; font-weight:700; }
.sky-chip { display:inline-block; margin-top:4px; padding:3px 10px; border-radius:8px;
  font-size:.78rem; background:rgba(255,255,255,.07); color:#EDE8F5 !important;
  text-decoration:none; }
.sky-rx { color:#E07A7A; font-size:.8rem; }
.sky-direct { color:#7FD1A0; font-size:.8rem; }
</style>
"""


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def safe_url(url) -> str:
    """Only allow http(s) links; anything else (or NaN) becomes empty."""
    if isinstance(url, str) and url.startswith(("https://", "http://")):
        return url
    return ""


def planet_rows(rows) -> str:
    """rows: list of (planet, position_text, is_retrograde)."""
    out = []
    for name, pos, retro in rows:
        status = '<span class="sky-rx">Rx</span>' if retro else '<span class="sky-direct">Direct</span>'
        out.append(
            f'<div class="sky-row"><span>{esc(name)}</span>'
            f'<span class="sky-muted">{esc(pos)}</span>{status}</div>'
        )
    return '<div class="sky-card">' + "".join(out) + "</div>"


def aspect_rows(aspects) -> str:
    """aspects: list of (planet_a, planet_b, aspect_name, orb)."""
    if not aspects:
        return '<div class="sky-card sky-muted">No major aspects within orb on this date.</div>'
    out = []
    for a, b, kind, orb in aspects:
        out.append(
            f'<div class="sky-row"><span>{esc(a)} &middot; {esc(b)}</span>'
            f'<span class="sky-muted">{esc(str(kind).title())}</span>'
            f'<span class="sky-score">{float(orb):.1f}&deg; orb</span></div>'
        )
    return '<div class="sky-card">' + "".join(out) + "</div>"


def echo_card(twin: dict) -> str:
    pct = f"{float(twin['score']) * 100:.1f}%"
    items = []
    for ev in twin["events"]:
        link = safe_url(ev.get("url"))
        chip = (f'<br><a class="sky-chip" href="{esc(link)}" target="_blank" '
                f'rel="noopener noreferrer">Wikipedia</a>') if link else ""
        items.append(f'<div style="margin-top:10px">{esc(ev["text"])}{chip}</div>')
    if not items:
        items = ['<div class="sky-muted" style="margin-top:10px">No events recorded for this date.</div>']
    return (
        '<div class="sky-card">'
        f'<div class="sky-row" style="border:none"><span class="sky-date">{esc(twin["date"])}</span>'
        f'<span class="sky-score">{pct} sky similarity</span></div>'
        '<div class="sky-muted">Closest sky geometry</div>'
        + "".join(items) + "</div>"
    )