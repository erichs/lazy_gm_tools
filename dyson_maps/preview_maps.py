#!/usr/bin/env python3
"""Generate an HTML preview gallery from Dyson map search results."""

import json
import os
import subprocess
import sys
import time
from html import escape

DYSON_DIR = os.path.dirname(os.path.abspath(__file__))
THUMBNAILS_DIR = os.path.join(DYSON_DIR, "thumbnails")
IMAGES_DIR = os.path.join(DYSON_DIR, "images")


def load_from_stdin():
    """Read JSON map results from stdin."""
    data = sys.stdin.read().strip()
    if not data:
        return {}
    return json.loads(data)


def load_from_keys(keys_csv):
    """Load specific maps by key from the YAML index."""
    import yaml

    index_path = os.path.join(DYSON_DIR, "map-index.yaml")
    with open(index_path) as f:
        all_maps = yaml.safe_load(f)["maps"]

    keys = [k.strip() for k in keys_csv.split(",") if k.strip()]
    return {k: all_maps[k] for k in keys if k in all_maps}


def thumbnail_path(key):
    """Get the file:// URL for a thumbnail."""
    path = os.path.join(THUMBNAILS_DIR, f"{key}_thumbnail.jpg")
    if os.path.exists(path):
        return f"file://{path}"
    return ""


def image_path(entry):
    """Get the file:// URL for the full image."""
    filename = entry.get("filename", "")
    if filename:
        path = os.path.join(IMAGES_DIR, filename)
        if os.path.exists(path):
            return f"file://{path}"
    return ""


def feature_pills(features):
    """Render feature list as HTML pills."""
    if not features:
        return ""
    return " ".join(f'<span class="pill">{escape(f)}</span>' for f in features[:8])


def combat_pills(combat_uses):
    """Render combat uses as HTML pills."""
    if not combat_uses:
        return ""
    return " ".join(f'<span class="pill combat">{escape(c)}</span>' for c in combat_uses)


def generate_card(key, entry):
    """Generate HTML for a single map card."""
    thumb = thumbnail_path(key)
    img = image_path(entry)
    name = escape(entry.get("name", key))
    map_type = escape(entry.get("type", ""))
    scale = escape(entry.get("scale", ""))
    rooms = entry.get("rooms", "?")
    chokepoints = entry.get("chokepoints", 0)
    atmosphere = escape(entry.get("atmosphere", ""))
    layout = escape(entry.get("layout", ""))
    desc = escape(entry.get("description", ""))
    features_html = feature_pills(entry.get("features", []))
    combat_html = combat_pills(entry.get("combat_use", []))
    gridded = "gridded" if entry.get("gridded") else "no grid"

    return f"""
    <div class="card" data-key="{escape(key)}">
      <a href="{img}" target="_blank">
        <img src="{thumb}" alt="{name}" loading="lazy">
      </a>
      <div class="info">
        <div class="name">{name}</div>
        <div class="badges">
          <span class="badge type">{map_type}</span>
          <span class="badge scale">{scale}</span>
          <span class="badge">{gridded}</span>
        </div>
        <div class="features">{features_html}</div>
      </div>
      <div class="overlay">
        <div><strong>Atmosphere:</strong> {atmosphere}</div>
        <div><strong>Layout:</strong> {layout}</div>
        <div><strong>Rooms:</strong> {rooms} &middot; <strong>Chokepoints:</strong> {chokepoints}</div>
        <div class="combat-uses">{combat_html}</div>
        <div class="desc">{desc}</div>
      </div>
    </div>"""


def generate_html(maps, query=None):
    """Generate the full HTML page."""
    count = len(maps)
    cards = "\n".join(generate_card(k, v) for k, v in maps.items())
    query_line = f'<div class="query">&ldquo;{escape(query)}&rdquo;</div>' if query else ""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Dyson Map Candidates ({count} results)</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1a2e; color: #e0e0e0; padding: 20px;
  }}
  h1 {{ text-align: center; margin-bottom: 5px; color: #e0e0e0; font-size: 1.4em; }}
  .subtitle {{ text-align: center; color: #888; margin-bottom: 4px; font-size: 0.9em; }}
  .query {{ text-align: center; color: #e94560; margin-bottom: 15px; font-size: 0.95em; font-style: italic; }}
  .controls {{
    text-align: center; padding: 10px 0 20px; position: sticky; top: 0;
    background: #1a1a2e; z-index: 10;
  }}
  .controls label {{ color: #aaa; margin-right: 10px; }}
  .controls input[type=range] {{ width: 300px; vertical-align: middle; }}
  .controls .size-val {{ color: #aaa; margin-left: 8px; }}
  .gallery {{
    display: flex; flex-wrap: wrap; gap: 12px; justify-content: center;
  }}
  .card {{
    position: relative; border-radius: 8px; overflow: hidden;
    background: #16213e; border: 1px solid #333; transition: border-color 0.2s;
  }}
  .card:hover {{ border-color: #e94560; }}
  .card img {{
    width: var(--thumb-size, 250px); height: auto; display: block;
    cursor: pointer;
  }}
  .info {{ padding: 6px 8px; }}
  .name {{
    font-weight: 600; font-size: 0.85em; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis; margin-bottom: 4px;
  }}
  .badges {{ display: flex; gap: 4px; flex-wrap: wrap; margin-bottom: 4px; }}
  .badge {{
    font-size: 0.65em; padding: 1px 6px; border-radius: 3px;
    background: #0f3460; color: #ccc;
  }}
  .badge.type {{ background: #e94560; color: #fff; }}
  .badge.scale {{ background: #533483; }}
  .features {{ display: flex; gap: 3px; flex-wrap: wrap; }}
  .pill {{
    font-size: 0.6em; padding: 1px 5px; border-radius: 3px;
    background: #1a3a5c; color: #aaa;
  }}
  .pill.combat {{ background: #5c1a1a; color: #e0a0a0; }}
  .overlay {{
    position: absolute; top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(10, 10, 30, 0.92); padding: 12px;
    opacity: 0; transition: opacity 0.2s; font-size: 0.75em;
    display: flex; flex-direction: column; gap: 4px;
    overflow-y: auto; pointer-events: none;
  }}
  .card:hover .overlay {{ opacity: 1; pointer-events: auto; }}
  .overlay .desc {{ margin-top: auto; font-style: italic; color: #aaa; }}
  .combat-uses {{ display: flex; gap: 3px; flex-wrap: wrap; }}
</style>
</head>
<body>
  <h1>Dyson Map Candidates</h1>
  <div class="subtitle">{count} maps found</div>
  {query_line}
  <div class="controls">
    <label for="sizeSlider">Thumbnail size:</label>
    <input type="range" id="sizeSlider" min="80" max="500" value="250">
    <span class="size-val" id="sizeVal">250px</span>
  </div>
  <div class="gallery">
    {cards}
  </div>
<script>
  const slider = document.getElementById('sizeSlider');
  const sizeVal = document.getElementById('sizeVal');
  const gallery = document.querySelector('.gallery');

  slider.addEventListener('input', function() {{
    gallery.style.setProperty('--thumb-size', this.value + 'px');
    sizeVal.textContent = this.value + 'px';
  }});
</script>
</body>
</html>"""


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate HTML preview of Dyson maps.")
    parser.add_argument("--maps", type=str, default=None, help="Comma-separated map keys")
    parser.add_argument("--query", type=str, default=None, help="Original natural-language search description")
    args = parser.parse_args()

    if args.maps:
        maps = load_from_keys(args.maps)
    elif not sys.stdin.isatty():
        maps = load_from_stdin()
    else:
        print("Provide map data via stdin (pipe from search_maps.py) or --maps flag.", file=sys.stderr)
        sys.exit(1)

    if not maps:
        print("No maps to preview.", file=sys.stderr)
        sys.exit(1)

    html = generate_html(maps, query=args.query)
    ts = int(time.time())
    out_path = f"/tmp/dyson-preview-{ts}.html"

    with open(out_path, "w") as f:
        f.write(html)

    print(out_path)
    subprocess.run(["open", out_path])


if __name__ == "__main__":
    main()
