#!/usr/bin/env python3
"""
Vision-based indexer for Dyson Logos map archive.
Sends each thumbnail to Gemini for structured classification.
Outputs a YAML index at dyson_maps/map-index.yaml.
"""

from google import genai
from google.genai import types
import os
import sys
import json
import glob
import time
import yaml

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not set")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)

THUMBNAIL_DIR = os.path.join(os.path.dirname(__file__), "thumbnails")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "map-index.yaml")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), ".index-progress.json")

CLASSIFICATION_PROMPT = """Analyze this fantasy RPG battle map thumbnail. Return ONLY valid JSON (no markdown, no commentary) with these fields:

{
  "type": "[primary type: dungeon|cave|temple|shrine|town|street|fort|fortress|sewer|tower|ruins|tavern|inn|tomb|crypt|manor|house|island|bridge|palace|monastery|mine|ship|outdoor|camp|village|cathedral|keep|spire|market|dock|library|prison|barracks|laboratory]",
  "setting": "[indoor|outdoor|underground|mixed]",
  "scale": "[small (1-3 rooms or areas)|medium (4-8 rooms)|large (9+ rooms)]",
  "rooms": [estimated number of distinct rooms/areas],
  "gridded": [true if visible grid squares, false otherwise],
  "features": ["list of notable map features from: water, lava, bridge, stairs, columns, altar, throne, cells, natural_cave, worked_stone, doors, secret_passage, pit, balcony, courtyard, garden, dock, ship, forest, cliff, river, well, fountain, statue, pool, fireplace, kitchen, bedroom, library, storage, workshop, gate, wall, battlement, arrow_slit, moat, drawbridge, portcullis, tower, spiral_stair, ladder, trapdoor, rubble, collapsed, overgrown, mushrooms, crystals, webs, bones, sarcophagus, coffin, pedestal, dais, circle, pentagram, furnace, anvil, cage, chains, pillars"],
  "layout": "[linear|branching|hub_and_spoke|open_plan|maze|loop|multi_level|single_room|corridor_based]",
  "chokepoints": [estimated number of narrow passages or defensible positions],
  "combat_use": ["list from: ambush, pitched_battle, siege, chase, boss_fight, skirmish, holdout, retreat, multi_front, arena, waves"],
  "atmosphere": "[from: ominous, sacred, utilitarian, natural, grand, cramped, eerie, ancient, military, domestic, arcane, ruined, infernal, aquatic, subterranean, pastoral, urban, industrial, royal, scholarly]",
  "description": "[one sentence describing the map layout and feel]"
}"""

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def classify_map(thumbnail_path, retries=3):
    with open(thumbnail_path, "rb") as f:
        image_bytes = f.read()

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[image_part, CLASSIFICATION_PROMPT],
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT"],
                    temperature=0.1,
                ),
            )
            text = response.candidates[0].content.parts[0].text.strip()
            # Strip markdown code fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text.rsplit("```", 1)[0]
                elif "```" in text:
                    text = text.rsplit("```", 1)[0]
            result = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(2)
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            if attempt < retries - 1:
                time.sleep(5)

    return None

def main():
    thumbnails = sorted(glob.glob(os.path.join(THUMBNAIL_DIR, "*_thumbnail.jpg")))
    print(f"Found {len(thumbnails)} thumbnails to classify")

    progress = load_progress()
    results = {}

    # Load any existing results from progress
    for key, val in progress.items():
        if val is not None:
            results[key] = val

    remaining = [t for t in thumbnails if os.path.basename(t) not in progress]
    print(f"Already classified: {len(progress)}, remaining: {len(remaining)}")

    for i, thumb_path in enumerate(remaining):
        thumb_name = os.path.basename(thumb_path)
        # Derive the full image filename
        map_name = thumb_name.replace("_thumbnail.jpg", "")

        # Find the actual image file (could be .png or .jpg)
        image_file = None
        for ext in [".png", ".jpg", ".jpeg"]:
            candidate = os.path.join(os.path.dirname(__file__), "images", map_name + ext)
            if os.path.exists(candidate):
                image_file = map_name + ext
                break

        print(f"[{len(progress)+i+1}/{len(thumbnails)}] {map_name}...", end=" ", flush=True)

        result = classify_map(thumb_path)
        if result:
            result["filename"] = image_file or map_name
            result["name"] = map_name.replace("-", " ").replace("_", " ").title()
            results[map_name] = result
            progress[thumb_name] = result
            print("OK")
        else:
            progress[thumb_name] = None
            print("FAILED")

        # Save progress every 10 maps
        if (i + 1) % 10 == 0:
            save_progress(progress)

        # Rate limit: ~15 requests per minute for free tier, be conservative
        time.sleep(1)

    save_progress(progress)

    # Write final YAML index
    index = {
        "version": 1,
        "total_maps": len(results),
        "generated": time.strftime("%Y-%m-%d"),
        "maps": results,
    }

    with open(OUTPUT_FILE, "w") as f:
        yaml.dump(index, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)

    print(f"\nDone! Wrote {len(results)} entries to {OUTPUT_FILE}")

    # Clean up progress file
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)

if __name__ == "__main__":
    main()
