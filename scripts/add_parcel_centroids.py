"""
DESHMRITTIKA / BHUMI-SYNC — Spatial Index Migration
Extracts centroid_lat and centroid_lon from coordinates_geojson for 100,000 parcels
and creates spatial index for sub-millisecond bounding box viewport queries.
Preserves all existing data, foreign keys, and tables.
"""

import sqlite3
import json
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "generated" / "full_scale" / "landtech_synthetic.db"

def main():
    print(f"[Spatial Migration] Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Check if columns already exist
    cur.execute("PRAGMA table_info(parcels)")
    existing_cols = [r[1] for r in cur.fetchall()]

    if "centroid_lat" not in existing_cols:
        print("[Spatial Migration] Adding centroid_lat column...")
        cur.execute("ALTER TABLE parcels ADD COLUMN centroid_lat REAL")
    if "centroid_lon" not in existing_cols:
        print("[Spatial Migration] Adding centroid_lon column...")
        cur.execute("ALTER TABLE parcels ADD COLUMN centroid_lon REAL")

    print("[Spatial Migration] Extracting centroids from coordinates_geojson...")
    cur.execute("SELECT parcel_id, coordinates_geojson FROM parcels WHERE centroid_lat IS NULL")
    rows = cur.fetchall()

    if rows:
        t0 = time.time()
        updates = []
        for pid, geo_str in rows:
            if geo_str:
                try:
                    g = json.loads(geo_str)
                    coords = g.get("coordinates", [[]])[0]
                    if coords:
                        lon = sum(pt[0] for pt in coords) / len(coords)
                        lat = sum(pt[1] for pt in coords) / len(coords)
                        updates.append((round(lat, 6), round(lon, 6), pid))
                except Exception:
                    pass

        print(f"[Spatial Migration] Updating {len(updates)} rows in batches...")
        cur.executemany("UPDATE parcels SET centroid_lat = ?, centroid_lon = ? WHERE parcel_id = ?", updates)
        conn.commit()
        print(f"[Spatial Migration] Centroids updated in {time.time() - t0:.2f}s")
    else:
        print("[Spatial Migration] Centroids already populated.")

    print("[Spatial Migration] Creating spatial index idx_parcels_spatial...")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parcels_spatial ON parcels (centroid_lon, centroid_lat)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_parcels_mouza_spatial ON parcels (mouza, centroid_lon, centroid_lat)")
    conn.commit()

    # Verify
    cur.execute("SELECT COUNT(*) FROM parcels WHERE centroid_lat IS NOT NULL")
    count = cur.fetchone()[0]
    print(f"[Spatial Migration] Successfully indexed {count} parcels.")

    # Test query performance
    t_q0 = time.time()
    cur.execute("""
        SELECT parcel_id, centroid_lat, centroid_lon FROM parcels
        WHERE centroid_lon BETWEEN 90.31 AND 90.33
          AND centroid_lat BETWEEN 23.79 AND 23.81
        LIMIT 50
    """)
    res = cur.fetchall()
    t_q1 = time.time()
    print(f"[Spatial Migration] Test bbox query returned {len(res)} results in {(t_q1 - t_q0)*1000:.2f}ms")

    conn.close()

if __name__ == "__main__":
    main()
