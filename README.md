# Industrial Telemetry Dashboard (original, runnable)

A small, dependency-light renderer that produces **original** animated telemetry panels for
industrial video and demos: UPS battery/load view, chiller approach view, and a generic
data-center view. No stock footage, no external model calls, no API keys.

Everything on screen is generated locally with Pillow and encoded with FFmpeg, and every clip
is labelled **ILLUSTRATIVE SAMPLE DATA** on the first line. The data is synthetic by design.

![preview](docs/preview.png)

## What it is

- A frame renderer (`dashboard.py`) that draws a dark operator UI: KPI tiles, an animated
  trend line, and an event feed.
- Three variants: `default` (rack inlet temperature), `ups` (battery state, runtime, string
  impedance drift), `chiller` (condenser approach, tower fan state).
- MP4 output at 1080x1920 or 1920x1080, cached by variant so repeated renders are free.

## What it is not

- It is **not** a monitoring product and it is **not** connected to any equipment.
- It does **not** read SNMP, Modbus or OPC-UA. It draws sample data.
- It makes **no** claim about battery failure prediction, savings or detection time.
- Nothing here controls, commands or writes to any industrial system.

If you need the real thing (read-only collection from your UPS, PCS, BMS or DCIM exports),
that is the engineering work: protocol support depends on your hardware and gateways.

## Requirements

- Python 3.9+
- Pillow
- FFmpeg on PATH

```bash
pip install -r requirements.txt
# Debian/Ubuntu: sudo apt-get install ffmpeg
```

## Usage

```python
from dashboard import make_dashboard

make_dashboard(portrait=True,  seconds=12, variant="ups")     # 1080x1920
make_dashboard(portrait=False, seconds=12, variant="chiller") # 1920x1080
```

Or from the CLI:

```bash
python dashboard.py          # renders one 6s clip per variant into /tmp/synqevra_dash
```

## Design notes

- Read-only by construction: the renderer only draws numbers passed to it.
- One accent colour (cyan) carries the data series; amber marks attention rows. Colour is
  used for meaning, not decoration.
- Text is sized against width so it stays readable on a phone.
- The "illustrative sample data" label is part of the frame, not an overlay that can be
  forgotten during editing.

## Licence

MIT. See `LICENSE`. Use it, fork it, change the labels for your own lab data.

## Contact

SYNQEVRA Solutions - Mr. Fatir Ali, Founder & Owner
Website: https://synqevrasolutions.github.io
Founder: https://synqevrasolutions.github.io/founder.html
Email: fatircompanyai@gmail.com
