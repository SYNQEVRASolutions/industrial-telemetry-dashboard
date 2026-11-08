"""Original animated telemetry dashboard clip - no stock footage.

Renders a dark UI panel with live-looking charts from SIMULATED sample data.
The clip is always labelled "illustrative sample data" so it is never mistaken
for a real customer screen.
"""
import hashlib
import math
import os
import random
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont

BG = (7, 13, 22)
PANEL = (11, 20, 32)
LINE = (23, 38, 58)
TEXT = (232, 242, 255)
MUTED = (143, 164, 184)
CYAN = (34, 211, 238)
AMBER = (251, 191, 36)
RED = (248, 113, 113)

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def _font(size, bold=True):
    for p in (FONT_CANDIDATES if bold else reversed(FONT_CANDIDATES)):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def _series(n, seed, base=21.4, drift=0.05):
    random.seed(seed)
    out, v = [], base
    for i in range(n):
        v += random.uniform(-drift, drift) + math.sin(i / 6.0) * 0.02
        out.append(round(v, 2))
    return out


VARIANTS = {
    "default": {"title": "Rack inlet temperature  \u00b7 last 60 min",
                "kpis": [("SUPPLY", "C", CYAN), ("ALARMS", "", AMBER)],
                "rows": [("21:04", "Supply temp above threshold for 6 min", AMBER),
                         ("20:58", "Unit B compressor short cycling", AMBER),
                         ("20:41", "Setpoint change by operator (approved)", MUTED)]},
    "ups": {"title": "UPS site 4  \u00b7 battery state and load",
            "kpis": [("BATTERY", "%", CYAN), ("RUNTIME", " min", AMBER)],
            "rows": [("21:04", "Battery string B impedance drifting up 9% over 30 days", AMBER),
                     ("20:58", "Load 64% on inverter A, transfer test due in 6 days", MUTED),
                     ("20:41", "Input voltage sag 3 events this week (read only)", MUTED)],
            "series_base": 92.0, "series_drift": 0.25},
    "chiller": {"title": "Chiller plant  \u00b7 approach temperature",
                "kpis": [("APPROACH", "C", CYAN), ("LOAD", "%", AMBER)],
                "rows": [("21:04", "Condenser approach 1.8C above baseline for 40 min", AMBER),
                         ("20:52", "Tower fan 2 running below expected speed", AMBER),
                         ("20:30", "Weekly efficiency report generated", MUTED)],
                "series_base": 3.2, "series_drift": 0.08},
}


def _frame(i, total, W, H, portrait, variant="default"):
    v = VARIANTS.get(variant, VARIANTS["default"])
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    pad = int(W * 0.06)
    f_small = _font(max(14, W // 62))
    f_h = _font(max(22, W // 30))
    f_kpi = _font(max(26, W // 22))
    f_lbl = _font(max(13, W // 68), bold=False)
    prog = min(1.0, i / max(1, total))

    d.text((pad, pad), "SYNQEVRA  /  ILLUSTRATIVE SAMPLE DATA", font=f_small, fill=CYAN)
    d.text((pad, pad + int(H * 0.045)), v["title"], font=f_h, fill=TEXT)

    ty = pad + int(H * 0.115)
    tw = (W - pad * 2 - int(W * 0.04)) // 2
    th = int(H * 0.105)
    if variant == "ups":
        val1 = f"{92.0 - prog * 4.5:.1f}%"
        val2 = f"{int(18 - prog * 3)} min"
    elif variant == "chiller":
        val1 = f"{3.2 + prog * 0.9:.1f} C"
        val2 = f"{int(62 + prog * 8)}%"
    else:
        val1 = f"{21.4 + math.sin(prog * 6) * 0.6:.1f} C"
        val2 = str(int(3 + prog * 2))
    kpis = [(v["kpis"][0][0], val1, v["kpis"][0][2]), (v["kpis"][1][0], val2, v["kpis"][1][2])]
    for k, (lbl, val, col) in enumerate(kpis):
        x = pad + k * (tw + int(W * 0.04))
        d.rounded_rectangle([x, ty, x + tw, ty + th], radius=14, fill=PANEL, outline=LINE)
        d.text((x + 18, ty + 12), lbl, font=f_lbl, fill=MUTED)
        d.text((x + 18, ty + int(th * 0.34)), val, font=f_kpi, fill=col)

    cy = ty + th + int(H * 0.05)
    ch = int(H * 0.30) if portrait else int(H * 0.42)
    d.rounded_rectangle([pad, cy, W - pad, cy + ch], radius=16, fill=PANEL, outline=LINE)
    gx0, gy0 = pad + 26, cy + 26
    gx1, gy1 = W - pad - 26, cy + ch - 26
    for g in range(5):
        y = gy0 + (gy1 - gy0) * g / 4
        d.line([gx0, y, gx1, y], fill=LINE, width=1)

    pts = _series(60, seed=7, base=v.get("series_base", 21.4), drift=v.get("series_drift", 0.05))
    lo, hi = min(pts) - 0.3, max(pts) + 0.3
    upto = max(2, int(60 * prog))
    xy = []
    for k in range(upto):
        x = gx0 + (gx1 - gx0) * k / 59
        y = gy1 - (gy1 - gy0) * (pts[k] - lo) / (hi - lo)
        xy.append((x, y))
    if len(xy) > 1:
        d.line(xy, fill=CYAN, width=max(3, W // 260), joint="curve")
        d.ellipse([xy[-1][0] - 6, xy[-1][1] - 6, xy[-1][0] + 6, xy[-1][1] + 6], fill=CYAN)

    fy = cy + ch + int(H * 0.045)
    shown = max(0, int(prog * 3.4))
    for r in range(min(shown, 3)):
        y = fy + r * int(H * 0.048)
        if y + 30 > H - pad:
            break
        t, msg, col = v["rows"][r]
        d.rounded_rectangle([pad, y, W - pad, y + int(H * 0.038)], radius=10, fill=PANEL, outline=LINE)
        d.text((pad + 16, y + 9), t, font=f_lbl, fill=col)
        d.text((pad + 92, y + 9), msg, font=f_lbl, fill=TEXT)
    return img


def make_dashboard(portrait=False, seconds=12, out_dir=None, fps=25, variant="default"):
    """Render the clip once and cache it. Returns the mp4 path or None."""
    W, H = (1080, 1920) if portrait else (1920, 1080)
    out_dir = out_dir or os.path.join(tempfile.gettempdir(), "synqevra_dash")
    os.makedirs(out_dir, exist_ok=True)
    key = hashlib.md5(f"{W}x{H}-{seconds}-{fps}-{variant}-v3".encode()).hexdigest()[:10]
    dest = os.path.join(out_dir, f"dashboard-{key}.mp4")
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        return dest

    tmp = os.path.join(out_dir, f"f-{key}")
    if os.path.exists(tmp):
        shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp, exist_ok=True)
    total = int(seconds * fps)
    for i in range(total):
        _frame(i, total, W, H, portrait, variant).save(os.path.join(tmp, f"{i:04d}.png"))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
           "-i", os.path.join(tmp, "%04d.png"), "-c:v", "libx264",
           "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", dest]
    subprocess.run(cmd, check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return dest if os.path.exists(dest) else None


if __name__ == "__main__":
    for var in ("default", "ups", "chiller"):
        p = make_dashboard(portrait=True, seconds=6, variant=var)
        print(var, "->", p, os.path.getsize(p) if p else 0)
