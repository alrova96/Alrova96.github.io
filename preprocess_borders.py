#!/usr/bin/env python3
"""Download country + US state boundaries, clip per terrain, save as JSON."""
import json, os, requests

OUT = os.path.join(os.path.dirname(__file__), "static", "terrain")

# Terrain bounding boxes (must match terrainCfg)
TERRAINS = {
    "cadiz":      {"w":-7.8,"e":-4.2,"s":34.4,"n":38.0},
    "malta":      {"w":12.9,"e":15.9,"s":34.4,"n":37.4},
    "nantes":     {"w":-3.1,"e":-0.1,"s":45.7,"n":48.7},
    "maryland":   {"w":-78.5,"e":-74.5,"s":37.0,"n":41.0},
    "finland":    {"w":28.0,"e":31.6,"s":60.8,"n":64.4},
    "valencia":   {"w":-1.9,"e":1.1,"s":38.0,"n":41.0},
    "jena":       {"w":10.1,"e":13.1,"s":49.4,"n":52.4},
    "bremerhaven":{"w":7.1,"e":10.1,"s":52.0,"n":55.0},
    "venice":     {"w":10.8,"e":13.8,"s":43.9,"n":46.9},
    "kent":       {"w":-82.8,"e":-79.8,"s":39.7,"n":42.7},
    "tromso":     {"w":17.0,"e":21.0,"s":67.6,"n":71.6},
    "antarctica": {"w":-62.0,"e":-58.0,"s":-64.0,"n":-61.0},
}

def clip_line(coords, bb, margin=0.5):
    """Clip a polyline to bounding box, returning list of segments inside."""
    w, e, s, n = bb["w"]-margin, bb["e"]+margin, bb["s"]-margin, bb["n"]+margin
    segments = []
    current = []
    for lon, lat in coords:
        inside = w <= lon <= e and s <= lat <= n
        if inside:
            current.append([round(lat,4), round(lon,4)])
        else:
            if len(current) >= 2:
                segments.append(current)
            current = []
    if len(current) >= 2:
        segments.append(current)
    return segments

def extract_lines(geojson, bb):
    """Extract all line segments from GeoJSON features within bounding box."""
    all_segs = []
    for feat in geojson.get("features", []):
        geom = feat.get("geometry", {})
        gtype = geom.get("type", "")
        coords_list = []
        if gtype == "LineString":
            coords_list = [geom["coordinates"]]
        elif gtype == "MultiLineString":
            coords_list = geom["coordinates"]
        elif gtype == "Polygon":
            coords_list = geom["coordinates"]  # rings
        elif gtype == "MultiPolygon":
            for poly in geom["coordinates"]:
                coords_list.extend(poly)
        for coords in coords_list:
            segs = clip_line(coords, bb)
            all_segs.extend(segs)
    return all_segs

def simplify_line(points, tolerance=0.02):
    """Simple Douglas-Peucker-like simplification."""
    if len(points) <= 2:
        return points
    # Find point with max distance from line between first and last
    first, last = points[0], points[-1]
    max_d, max_i = 0, 0
    for i in range(1, len(points)-1):
        p = points[i]
        # Perpendicular distance
        dx, dy = last[0]-first[0], last[1]-first[1]
        if dx == 0 and dy == 0:
            d = ((p[0]-first[0])**2 + (p[1]-first[1])**2)**0.5
        else:
            d = abs(dy*p[0] - dx*p[1] + last[0]*first[1] - last[1]*first[0]) / (dx**2+dy**2)**0.5
        if d > max_d:
            max_d, max_i = d, i
    if max_d > tolerance:
        left = simplify_line(points[:max_i+1], tolerance)
        right = simplify_line(points[max_i:], tolerance)
        return left[:-1] + right
    return [first, last]

print("Downloading border data...")
# Country borders (boundary lines, not polygons - much cleaner)
countries_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_boundary_lines_land.geojson"
countries = requests.get(countries_url, timeout=30).json()
print(f"  Countries: {len(countries['features'])} features")

# Also get country polygons for coastlines
coast_url = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_coastline.geojson"
coast = requests.get(coast_url, timeout=30).json()
print(f"  Coastlines: {len(coast['features'])} features")

# US states (polygons - we extract outlines as borders)
states_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states = requests.get(states_url, timeout=30).json()
print(f"  US States: {len(states['features'])} features")

for tid, bb in TERRAINS.items():
    borders = extract_lines(countries, bb)
    coasts = extract_lines(coast, bb)

    # For US terrains, also add state borders
    state_lines = []
    if bb["w"] < -50:  # Western hemisphere = Americas
        state_lines = extract_lines(states, bb)

    # Simplify all lines
    all_lines = []
    for seg in borders:
        s = simplify_line(seg, 0.015)
        if len(s) >= 2:
            all_lines.append({"t": "border", "pts": s})
    for seg in state_lines:
        s = simplify_line(seg, 0.015)
        if len(s) >= 2:
            all_lines.append({"t": "state", "pts": s})

    outpath = os.path.join(OUT, f"{tid}_borders.json")
    with open(outpath, "w") as f:
        json.dump(all_lines, f, separators=(",", ":"))

    nb = sum(1 for l in all_lines if l["t"]=="border")
    ns = sum(1 for l in all_lines if l["t"]=="state")
    print(f"  {tid}: {nb} border lines, {ns} state lines, {os.path.getsize(outpath)//1024}KB")

print("Done!")
