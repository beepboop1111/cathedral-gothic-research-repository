#!/usr/bin/env python3
"""Create standalone zoomed analytic SVG from the full-page R04 tracing."""
from pathlib import Path
import cairosvg
P=Path(__file__).resolve().parent
s=(P/'02_MEASURED_LOBE_ARCS.svg').read_text()
(P/'05_FULL_WINDOW_WITH_MEASURED_ARCS.svg').write_text(s)
zoom=s.replace('width="1563" height="1996" viewBox="0 0 1563 1996"', 'width="800" height="800" viewBox="310 490 340 340"')
(P/'06_MASTER_CLOSEUP_CONSTRUCTION.svg').write_text(zoom)
cairosvg.svg2png(bytestring=zoom.encode(),write_to=str(P/'06_MASTER_CLOSEUP_CONSTRUCTION.png'),output_width=850,output_height=850)
