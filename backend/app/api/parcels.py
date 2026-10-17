"""
DESHMRITTIKA / BHUMI-SYNC — Linked Parcel Profile & Spatial Map Endpoints (P6 Track)
Supports:
- Viewport Bounding-Box Parcel Map Retrieval (GeoJSON FeatureCollection)
- Single Parcel Location & Administrative Grounding
- Spatial Layers for Gazetted Acquisition Corridors & Government Khas Land
- Single Parcel Full Relational Profile & Individual GeoJSON
"""

import sqlite3
import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from backend.app.database import get_db
from backend.app.schemas.models import ParcelDetail
from backend.app.services.parcel_profile import ParcelProfileService
from backend.app.services.due_diligence import DueDiligenceService

router = APIRouter(prefix="/parcels", tags=["Parcels & Spatial GIS"])

MAP_DISCLAIMER = "DEMO DATA — NOT AN OFFICIAL LAND SURVEY. Bounding polygons and coordinates are synthetic cadastral visualizations for demonstration."


@router.get("/layers/acquisition-zones")
def get_acquisition_zones_geojson(db: sqlite3.Connection = Depends(get_db)):
    """Returns GeoJSON FeatureCollection of all gazetted acquisition corridors."""
    cur = db.cursor()
    cur.execute("SELECT zone_id, project_name, gazette_notification_no, corridor_geojson, status FROM acquisition_zones")
    rows = cur.fetchall()

    features = []
    for r in rows:
        try:
            geom = json.loads(r["corridor_geojson"])
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "zone_id": r["zone_id"],
                    "project_name": r["project_name"],
                    "gazette_notification_no": r["gazette_notification_no"],
                    "status": r["status"],
                    "layer_type": "GOVERNMENT_ACQUISITION_CORRIDOR",
                    "provenance": "GAZETTED_INFRASTRUCTURE_CORRIDOR"
                }
            })
        except Exception:
            pass

    collection = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "total_corridors": len(features),
            "disclaimer": MAP_DISCLAIMER
        }
    }
    return Response(content=json.dumps(collection, ensure_ascii=False), media_type="application/geo+json")


@router.get("/layers/khas-land")
def get_khas_land_geojson(
    bbox: Optional[str] = Query(None, description="min_lon,min_lat,max_lon,max_lat"),
    limit: int = Query(50, ge=1, le=200),
    db: sqlite3.Connection = Depends(get_db)
):
    """Returns GeoJSON FeatureCollection of government 1-No. Khas land parcels."""
    cur = db.cursor()
    query = """
        SELECT k.khas_id, k.khas_category, k.managing_authority,
               p.parcel_id, p.mouza, p.dag_number, p.area_decimal, p.coordinates_geojson
        FROM khas_records k
        JOIN parcels p ON k.parcel_id = p.parcel_id
        WHERE p.coordinates_geojson IS NOT NULL
        LIMIT ?
    """
    cur.execute(query, (limit,))
    rows = cur.fetchall()

    features = []
    for r in rows:
        try:
            geom = json.loads(r["coordinates_geojson"])
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "khas_id": r["khas_id"],
                    "parcel_id": r["parcel_id"],
                    "category": r["khas_category"],
                    "authority": r["managing_authority"],
                    "mouza": r["mouza"],
                    "dag_number": r["dag_number"],
                    "area_decimal": r["area_decimal"],
                    "layer_type": "GOVERNMENT_KHAS_LAND",
                    "is_protected": True
                }
            })
        except Exception:
            pass

    collection = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "total_khas_parcels": len(features),
            "disclaimer": MAP_DISCLAIMER
        }
    }
    return Response(content=json.dumps(collection, ensure_ascii=False), media_type="application/geo+json")


@router.get("/map")
def get_parcels_map(
    bbox: Optional[str] = Query(None, description="min_lon,min_lat,max_lon,max_lat"),
    mouza: Optional[str] = Query(None, description="Filter by mouza name"),
    limit: int = Query(100, ge=1, le=500),
    db: sqlite3.Connection = Depends(get_db)
):
    """Viewport-based retrieval of parcel geometries to avoid loading 100,000 parcels at once."""
    cur = db.cursor()

    query = """
        SELECT parcel_id, mouza, jl_number, dag_number, khatian_number,
               area_decimal, is_disputed, coordinates_geojson, centroid_lat, centroid_lon
        FROM parcels
        WHERE coordinates_geojson IS NOT NULL
    """
    params = []

    if mouza:
        query += " AND mouza LIKE ?"
        params.append(f"%{mouza.strip()}%")

    min_lon, min_lat, max_lon, max_lat = None, None, None, None
    if bbox:
        try:
            parts = [float(x.strip()) for x in bbox.split(",")]
            if len(parts) == 4:
                min_lon, min_lat, max_lon, max_lat = parts
                query += " AND centroid_lon BETWEEN ? AND ? AND centroid_lat BETWEEN ? AND ?"
                params.extend([min_lon, max_lon, min_lat, max_lat])
        except Exception:
            pass

    query += " LIMIT ?"
    params.append(limit)

    cur.execute(query, params)
    rows = cur.fetchall()

    features = []
    for r in rows:
        try:
            geom = json.loads(r["coordinates_geojson"])

            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "parcel_id": r["parcel_id"],
                    "mouza": r["mouza"],
                    "jl_number": r["jl_number"],
                    "dag_number": r["dag_number"],
                    "khatian_number": r["khatian_number"],
                    "area_decimal": r["area_decimal"],
                    "is_disputed": bool(r["is_disputed"]),
                    "provenance": "SYNTHETIC_DEMO_PARCEL"
                }
            })
            if len(features) >= limit:
                break
        except Exception:
            pass

    collection = {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "returned_count": len(features),
            "bbox_filter_applied": bool(min_lon is not None),
            "disclaimer": MAP_DISCLAIMER
        }
    }
    return Response(content=json.dumps(collection, ensure_ascii=False), media_type="application/geo+json")


@router.get("/{parcel_id}/location")
def get_parcel_location(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns normalized administrative location, centroid, and geometry status for a parcel."""
    cur = db.cursor()
    cur.execute("""
        SELECT parcel_id, district, upazila, mouza, jl_number, dag_number,
               khatian_number, area_decimal, land_classification, is_disputed,
               coordinates_geojson, provenance_label
        FROM parcels
        WHERE parcel_id = ?
    """, (parcel_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="পার্সেল খুঁজে পাওয়া যায়নি (Parcel not found).")

    has_geom = bool(row["coordinates_geojson"])
    geom = None
    centroid = None
    if has_geom:
        try:
            geom = json.loads(row["coordinates_geojson"])
            coords = geom["coordinates"][0]
            # Centroid calculation
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            centroid = {
                "latitude": round(sum(lats) / len(lats), 6),
                "longitude": round(sum(lons) / len(lons), 6)
            }
        except Exception:
            has_geom = False

    # Get quick due diligence rating
    dossier = DueDiligenceService.generate_buyer_dossier(db, parcel_id)
    rating = dossier.safety_rating if dossier else "UNKNOWN"
    risk_score = dossier.risk_score if dossier else 0

    return {
        "parcel_id": row["parcel_id"],
        "district": row["district"],
        "upazila": row["upazila"],
        "mouza": row["mouza"],
        "jl_number": row["jl_number"],
        "administrative_hierarchy": {
            "division": "Dhaka",
            "district": row["district"],
            "upazila": row["upazila"],
            "mouza": row["mouza"],
            "jl_number": row["jl_number"]
        },
        "dag_number": row["dag_number"],
        "khatian_number": row["khatian_number"],
        "area_decimal": float(row["area_decimal"]),
        "land_classification": row["land_classification"],
        "is_disputed": bool(row["is_disputed"]),
        "has_geometry": has_geom,
        "geometry": geom,
        "boundary_polygon": geom,
        "centroid": centroid,
        "location_status": "SYNTHETIC_CADASTRAL_POLYGON" if has_geom else "LOCATION_UNAVAILABLE",
        "due_diligence_summary": {
            "safety_rating": rating,
            "risk_score": risk_score,
            "is_government_khas": dossier.is_government_khas if dossier else False,
            "unmutated_deeds_count": dossier.unmutated_deeds_count if dossier else 0
        },
        "provenance": row["provenance_label"],
        "disclaimer": MAP_DISCLAIMER
    }


@router.get("/{parcel_id}", response_model=ParcelDetail)
def get_parcel_profile(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns full 14-entity relational profile for a parcel."""
    profile = ParcelProfileService.get_parcel_profile(db, parcel_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Parcel with ID '{parcel_id}' not found.")
    return profile


@router.get("/{parcel_id}/geojson")
def get_parcel_geojson(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    """Returns compliant GeoJSON Feature for an individual parcel."""
    cur = db.cursor()
    cur.execute("SELECT coordinates_geojson, parcel_id, mouza, dag_number FROM parcels WHERE parcel_id = ?", (parcel_id,))
    row = cur.fetchone()
    if not row or not row["coordinates_geojson"]:
        raise HTTPException(status_code=404, detail="Parcel geometry not found.")

    geometry = json.loads(row["coordinates_geojson"])
    feature = {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "parcel_id": row["parcel_id"],
            "mouza": row["mouza"],
            "dag_number": row["dag_number"],
            "provenance": "SYNTHETIC_CADASTRAL_VISUALIZATION"
        }
    }
    return Response(content=json.dumps(feature), media_type="application/geo+json")
