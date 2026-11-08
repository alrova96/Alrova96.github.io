#!/usr/bin/env python3
"""
Download real elevation/bathymetry data from Mapzen Terrarium tiles (ETOPO+SRTM)
and generate .json + .bin terrain files for the 3D globe terrain deployment.
Format matches the atlas terrain system.
"""
import math, struct, json, os, sys
import numpy as np
import requests
from PIL import Image
from io import BytesIO

TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
OUT_DIR = os.path.join(os.path.dirname(__file__), "static", "terrain")
os.makedirs(OUT_DIR, exist_ok=True)

# Locations: id, lat, lon, half-size in degrees, exaggeration factor
SITES = [
    {"id": "cadiz",      "lat": 36.2,  "lon": -6.0,   "span": 1.8, "exag": 6,  "ice": False},
    {"id": "malta",      "lat": 35.9,  "lon": 14.4,   "span": 1.5, "exag": 5,  "ice": False},
    {"id": "nantes",     "lat": 47.2,  "lon": -1.6,   "span": 1.5, "exag": 5,  "ice": False},
    {"id": "maryland",   "lat": 39.0,  "lon": -76.5,  "span": 2.0, "exag": 5,  "ice": False},
    {"id": "finland",    "lat": 62.6,  "lon": 29.8,   "span": 1.8, "exag": 5,  "ice": False},
    {"id": "valencia",   "lat": 39.5,  "lon": -0.4,   "span": 1.5, "exag": 5,  "ice": False},
    {"id": "jena",       "lat": 50.9,  "lon": 11.6,   "span": 1.5, "exag": 5,  "ice": False},
    {"id": "bremerhaven","lat": 53.5,  "lon": 8.6,    "span": 1.5, "exag": 5,  "ice": False},
    {"id": "venice",     "lat": 45.4,  "lon": 12.3,   "span": 1.5, "exag": 5,  "ice": False},
    {"id": "kent",       "lat": 41.2,  "lon": -81.3,  "span": 1.5, "exag": 5,  "ice": False},
    {"id": "tromso",     "lat": 69.6,  "lon": 19.0,   "span": 2.0, "exag": 4,  "ice": False},
    {"id": "antarctica", "lat": -62.8, "lon": -60.5,  "span": 2.0, "exag": 4,  "ice": True},
]

TARGET_COLS = 200  # grid resolution


def deg2tile(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def tile2deg(x, y, z):
    """Top-left corner of tile in degrees."""
    n = 2 ** z
    lon = x / n * 360 - 180
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    return lat, lon


def download_tile(z, x, y):
    url = TILE_URL.format(z=z, x=x, y=y)
    r = requests.get(url, timeout=15)
    if r.status_code != 200:
        return None
    return np.array(Image.open(BytesIO(r.content)))


def terrarium_decode(img):
    """Decode Terrarium-encoded elevation: (R*256 + G + B/256) - 32768"""
    return img[:, :, 0].astype(np.float64) * 256 + img[:, :, 1].astype(np.float64) + img[:, :, 2].astype(np.float64) / 256 - 32768


def process_site(site):
    sid = site["id"]
    lat, lon, span = site["lat"], site["lon"], site["span"]
    west = lon - span
    east = lon + span
    south = lat - span
    north = lat + span

    print(f"  Processing {sid}: ({south:.1f},{west:.1f}) to ({north:.1f},{east:.1f})")

    # Choose zoom level: ~4-5km per pixel for reasonable detail
    z = 7
    tile_min_x, tile_max_y = deg2tile(south, west, z)
    tile_max_x, tile_min_y = deg2tile(north, east, z)

    # Ensure we cover the whole area
    tile_min_x = max(0, tile_min_x - 1)
    tile_max_x = min(2**z - 1, tile_max_x + 1)
    tile_min_y = max(0, tile_min_y - 1)
    tile_max_y = min(2**z - 1, tile_max_y + 1)

    # Download and stitch tiles
    ntx = tile_max_x - tile_min_x + 1
    nty = tile_max_y - tile_min_y + 1
    full = np.zeros((nty * 256, ntx * 256, 3), dtype=np.uint8)

    for ty in range(tile_min_y, tile_max_y + 1):
        for tx in range(tile_min_x, tile_max_x + 1):
            img = download_tile(z, tx, ty)
            if img is None:
                print(f"    Warning: tile {z}/{tx}/{ty} not found")
                continue
            iy = ty - tile_min_y
            ix = tx - tile_min_x
            full[iy*256:(iy+1)*256, ix*256:(ix+1)*256, :] = img[:, :, :3]

    # Decode elevation
    elev_full = terrarium_decode(full)

    # Calculate pixel bounds for our bounding box
    top_lat, left_lon = tile2deg(tile_min_x, tile_min_y, z)
    bot_lat, right_lon_dummy = tile2deg(tile_min_x, tile_max_y + 1, z)
    dummy_lat, right_lon = tile2deg(tile_max_x + 1, tile_min_y, z)

    h_full, w_full = elev_full.shape
    px_west = int((west - left_lon) / (right_lon - left_lon) * w_full)
    px_east = int((east - left_lon) / (right_lon - left_lon) * w_full)
    px_north = int((top_lat - north) / (top_lat - bot_lat) * h_full)
    px_south = int((top_lat - south) / (top_lat - bot_lat) * h_full)

    px_west = max(0, px_west)
    px_east = min(w_full, px_east)
    px_north = max(0, px_north)
    px_south = min(h_full, px_south)

    cropped = elev_full[px_north:px_south, px_west:px_east]
    if cropped.size == 0:
        print(f"    ERROR: empty crop for {sid}")
        return

    # Resample to target resolution
    from PIL import Image as PILImage
    rows_target = int(TARGET_COLS * cropped.shape[0] / cropped.shape[1])
    img_elev = PILImage.fromarray(cropped.astype(np.float32), mode='F')
    img_resampled = img_elev.resize((TARGET_COLS, rows_target), PILImage.BILINEAR)
    grid = np.array(img_resampled)

    # Clamp extreme values
    grid = np.clip(grid, -11000, 9000)

    # Save binary (Int16, row-major, north to south)
    grid_i16 = grid.astype(np.int16)
    bin_path = os.path.join(OUT_DIR, f"{sid}.bin")
    with open(bin_path, "wb") as f:
        f.write(grid_i16.tobytes())

    meta = {
        "cols": TARGET_COLS,
        "rows": rows_target,
        "west": round(west, 4),
        "east": round(east, 4),
        "south": round(south, 4),
        "north": round(north, 4),
        "min": int(grid_i16.min()),
        "max": int(grid_i16.max()),
    }
    json_path = os.path.join(OUT_DIR, f"{sid}.json")
    with open(json_path, "w") as f:
        json.dump(meta, f)

    print(f"    Done: {TARGET_COLS}x{rows_target}, elev [{meta['min']}m, {meta['max']}m], "
          f"bin={os.path.getsize(bin_path)//1024}KB")


if __name__ == "__main__":
    print("Downloading terrain data for all locations...")
    for site in SITES:
        try:
            process_site(site)
        except Exception as e:
            print(f"    ERROR processing {site['id']}: {e}")
    print("\nDone! Terrain files saved to static/terrain/")
