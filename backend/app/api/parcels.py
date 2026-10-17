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


@router.get("/{parcel_id}/chain-of-title")
def get_parcel_chain_of_title(parcel_id: str, db: sqlite3.Connection = Depends(get_db)):
    """
    Returns structured, chronological Chain of Title (বায়া দলিল ধারাবাহিকতা ও মালিকানা শৃঙ্খল)
    for visual timeline rendering.
    """
    cur = db.cursor()
    cur.execute("""
        SELECT parcel_id, district, upazila, mouza, jl_number, dag_number,
               khatian_number, survey_type, land_classification, area_decimal,
               is_disputed, coordinates_geojson, provenance_label
        FROM parcels
        WHERE parcel_id = ?
    """, (parcel_id,))
    p = cur.fetchone()
    if not p:
        raise HTTPException(status_code=404, detail="পার্সেল পাওয়া যায়নি (Parcel not found).")

    # Fetch deeds
    cur.execute("""
        SELECT d.deed_id, d.deed_number, d.sub_registry_office, d.deed_type,
               d.execution_date, d.registration_date, d.declared_area, d.deed_value_bdt,
               d.deed_status, s.fictional_name as seller_name, b.fictional_name as buyer_name
        FROM deeds d
        JOIN owners s ON d.seller_id = s.owner_id
        JOIN owners b ON d.buyer_id = b.owner_id
        WHERE d.parcel_id = ?
        ORDER BY d.registration_date ASC
    """, (parcel_id,))
    deeds = [dict(r) for r in cur.fetchall()]

    # Fetch mutations
    cur.execute("""
        SELECT m.mutation_id, m.case_number, m.application_date, m.status,
               m.decision_date, m.mutated_khatian_no, o.fictional_name as applicant_name,
               d.deed_number
        FROM mutation_records m
        JOIN owners o ON m.applicant_id = o.owner_id
        JOIN deeds d ON m.deed_id = d.deed_id
        WHERE m.parcel_id = ?
        ORDER BY m.application_date ASC
    """, (parcel_id,))
    mutations = [dict(r) for r in cur.fetchall()]

    # Fetch ownership records
    cur.execute("""
        SELECT po.ownership_id, po.ownership_share, po.valid_from, po.valid_to,
               o.fictional_name, o.contact_masked, o.synthetic_nid_hash
        FROM parcel_ownership po
        JOIN owners o ON po.owner_id = o.owner_id
        WHERE po.parcel_id = ?
        ORDER BY po.valid_from ASC
    """, (parcel_id,))
    owners = [dict(r) for r in cur.fetchall()]

    # Fetch verification cases / conflicts
    cur.execute("""
        SELECT case_id, finding_code, risk_score, severity, review_status, explanation_bn
        FROM verification_cases
        WHERE parcel_id = ?
        ORDER BY risk_score DESC
    """, (parcel_id,))
    conflicts = [dict(r) for r in cur.fetchall()]

    # Construct chronological timeline events
    events = []
    event_counter = 1

    # 1. Historical Survey Baseline (CS/SA/RS)
    events.append({
        "event_id": f"EV-{event_counter:03d}",
        "year": "১৯৪০",
        "date_approx": "1940-01-01",
        "record_type": "CS",
        "record_type_label": "সিএস রেকর্ড (Cadastral Survey)",
        "event_type": "SURVEY_RECORD",
        "icon": "🏛️",
        "badge_class": "badge-forest",
        "title_bn": f"সিএস খতিয়ান মূল রেকর্ড — দাগ নং {p['dag_number']}",
        "owner_name": owners[0]["fictional_name"] if owners else "মৌলভী করিম বখশ (পূর্বতন মালিক)",
        "dag_khatian_ref": f"সিএস খতিয়ান: ৪২, দাগ: {p['dag_number']}",
        "recorded_area_decimal": float(p["area_decimal"]),
        "document_ref": "জেলা কালেক্টরেট সিএস রেকর্ড রুম ভলিউম-১২",
        "status_bn": "মূল ঐতিহাসিক রেকর্ড",
        "is_conflict": False,
        "evidence_type": "সরকারি জরিপ পরচা",
        "narrative_bn": "তৎকালীন বঙ্গীয় প্রজাস্বত্ব আইন (Tenancy Act 1885) মোতাবেক প্রস্তুতকৃত আদি সিএস খতিয়ান।"
    })
    event_counter += 1

    events.append({
        "event_id": f"EV-{event_counter:03d}",
        "year": "১৯৬২",
        "date_approx": "1962-04-15",
        "record_type": "SA",
        "record_type_label": "এসএ রেকর্ড (State Acquisition)",
        "event_type": "SURVEY_RECORD",
        "icon": "🏛️",
        "badge_class": "badge-forest",
        "title_bn": f"এসএ রেকর্ড ও ওয়ারিশান হস্তান্তর — দাগ নং {p['dag_number']}",
        "owner_name": "ওয়ারিশ সূত্রে স্বত্বাধিকারী",
        "dag_khatian_ref": f"এসএ খতিয়ান: ১২৮, দাগ: {p['dag_number']}",
        "recorded_area_decimal": float(p["area_decimal"]),
        "document_ref": "উপজেলা ভূমি রেকর্ড রুম (SATA 1950)",
        "status_bn": "অবিচ্ছিন্ন উত্তরাধিকার",
        "is_conflict": False,
        "evidence_type": "এসএ রিকুইজিশন খতিয়ান",
        "narrative_bn": "জমিদারি উচ্ছেদ ও প্রজাস্বত্ব আইন ১৯৫০ অনুযায়ী ওয়ারিশ সূত্রে ধারাবাহিক মালিকানা প্রতিষ্ঠিত।"
    })
    event_counter += 1

    # 2. Add Deeds
    for d in deeds:
        is_conflicting = any(c["finding_code"] in ["DS-01", "DS-03"] for c in conflicts) and ("2023" in d.get("registration_date", "") or "2024" in d.get("registration_date", ""))
        events.append({
            "event_id": f"EV-{event_counter:03d}",
            "year": d["registration_date"][:4] if d.get("registration_date") else "২০১৬",
            "date_approx": d.get("registration_date", ""),
            "record_type": "RS/BS",
            "record_type_label": f"সাব-রেজিস্ট্রি দলিল ({d['deed_type']})",
            "event_type": "DEED_TRANSFER",
            "icon": "⚠️" if is_conflicting else "🤝",
            "badge_class": "badge-danger" if is_conflicting else "badge-sky",
            "title_bn": f"সাফ-কবালা বিক্রয় দলিল নং {d['deed_number']}",
            "owner_name": f"বিক্রেতা: {d['seller_name']} ➔ ক্রেতা: {d['buyer_name']}",
            "dag_khatian_ref": f"দাগ: {p['dag_number']}, সাব-রেজিস্ট্রি: {d['sub_registry_office']}",
            "recorded_area_decimal": float(d.get("declared_area", p["area_decimal"])),
            "document_ref": f"দলিল নং {d['deed_number']}, সাব-রেজিস্ট্রি বই ভলিউম নং ৪২",
            "status_bn": "সন্দেহজনক দ্বৈত হস্তান্তর" if is_conflicting else "বৈধভাবে নিবন্ধিত",
            "is_conflict": is_conflicting,
            "evidence_type": "সাব-রেজিস্ট্রি সাফ-কবালা বালাম",
            "narrative_bn": "পূর্বে হস্তান্তরিত জমি গোপন রেখে পুনরায় বিক্রয় চেষ্টা।" if is_conflicting else f"মূল্য: ৳ {d.get('deed_value_bdt', 0):,} টাকা পরিশোধপূর্বক রেজিস্ট্রিকৃত হস্তান্তরিত সম্পত্তি।"
        })
        event_counter += 1

    # 3. Add Mutations
    for m in mutations:
        is_approved = (m.get("status") == "APPROVED")
        events.append({
            "event_id": f"EV-{event_counter:03d}",
            "year": m["decision_date"][:4] if m.get("decision_date") else "২০১৭",
            "date_approx": m.get("decision_date", ""),
            "record_type": "BS",
            "record_type_label": "সহকারী কমিশনার (ভূমি) নামজারি",
            "event_type": "MUTATION_APPROVAL" if is_approved else "MUTATION_PENDING",
            "icon": "🔄" if is_approved else "⏳",
            "badge_class": "badge-forest" if is_approved else "badge-warning",
            "title_bn": f"ই-নামজারি ও জমাভাগ কেস নং {m['case_number']}",
            "owner_name": f"আবেদনকারী: {m['applicant_name']}",
            "dag_khatian_ref": f"খারিজ খতিয়ান নং: {m.get('mutated_khatian_no', p['khatian_number'])}, দাগ: {p['dag_number']}",
            "recorded_area_decimal": float(p["area_decimal"]),
            "document_ref": f"নামজারি কেস {m['case_number']} (সহকারী কমিশনার - ভূমি কার্যালয়)",
            "status_bn": "অনুমোদিত ও রেকর্ড সংশোধিত" if is_approved else "অনিষ্পন্ন / প্রক্রিয়াধীন",
            "is_conflict": not is_approved,
            "evidence_type": "ডিজিটাল নামজারি ডিসিআর ও খতিয়ান",
            "narrative_bn": f"অনুমোদন সাপেক্ষে হালনাগাদ ১নং খতিয়ান হতে কর্তনপূর্বক নতুন খতিয়ান নং {m.get('mutated_khatian_no', p['khatian_number'])} সৃজিত।"
        })
        event_counter += 1

    # 4. If any unresolved conflict, add conflict banner event
    for c in conflicts:
        events.append({
            "event_id": f"EV-{event_counter:03d}",
            "year": "২০২৪",
            "date_approx": "2024-03-01",
            "record_type": "ALERT",
            "record_type_label": f"এআই স্ক্রিনিং অসঙ্গতি ({c['finding_code']})",
            "event_type": "CONFLICT_ALERT",
            "icon": "🚨",
            "badge_class": "badge-danger",
            "title_bn": f"ঝুঁকি অ্যালার্ট: {c['finding_code']} — {c['severity']}",
            "owner_name": "তদন্তাধীন রেকর্ড",
            "dag_khatian_ref": f"দাগ: {p['dag_number']}, কেস: {c['case_id']}",
            "recorded_area_decimal": float(p["area_decimal"]),
            "document_ref": f"ভেরিফিকেশন কেস {c['case_id']}",
            "status_bn": "ট্রায়াজ তদন্তাধীন",
            "is_conflict": True,
            "evidence_type": "স্বয়ংক্রিয় অডিট অ্যালার্ট",
            "narrative_bn": c.get("explanation_bn", "")
        })
        event_counter += 1

    return {
        "parcel_id": p["parcel_id"],
        "parcel": {
            "parcel_id": p["parcel_id"],
            "district": p["district"],
            "upazila": p["upazila"],
            "mouza": p["mouza"],
            "jl_number": p["jl_number"],
            "dag_number": p["dag_number"],
            "khatian_number": p["khatian_number"],
            "area_decimal": float(p["area_decimal"]),
            "land_classification": p["land_classification"],
            "survey_type": p["survey_type"],
            "is_disputed": bool(p["is_disputed"]),
            "provenance": p["provenance_label"]
        },
        "parcel_summary": {
            "parcel_id": p["parcel_id"],
            "district": p["district"],
            "upazila": p["upazila"],
            "mouza": p["mouza"],
            "jl_number": p["jl_number"],
            "dag_number": p["dag_number"],
            "khatian_number": p["khatian_number"],
            "area_decimal": float(p["area_decimal"]),
            "land_classification": p["land_classification"],
            "survey_type": p["survey_type"],
            "is_disputed": bool(p["is_disputed"]),
            "provenance": p["provenance_label"]
        },
        "total_events": len(events),
        "timeline": events,
        "timeline_events": events,
        "area_summary": {
            "original_area_decimal": float(p["area_decimal"]),
            "total_transferred_decimal": float(deeds[0]["declared_area"]) if deeds else float(p["area_decimal"]),
            "current_retained_decimal": float(p["area_decimal"]),
            "unit": "শতক (decimal)"
        },
        "area_transition_summary": {
            "original_recorded_area": float(p["area_decimal"]),
            "transferred_area": float(deeds[0]["declared_area"]) if deeds else float(p["area_decimal"]),
            "retained_balance": float(p["area_decimal"]),
            "unit": "শতক (decimal)"
        },
        "document_references": [
            {
                "label": "সিএস রেকর্ড রুম নথি",
                "ref": f"CS-KHATIAN-42-{p['dag_number']}",
                "status": "VERIFIED_ARCHIVE",
                "doc_type": "CS_KHATIAN",
                "doc_number": f"CS-KHATIAN-42-{p['dag_number']}",
                "registry_office": "ঢাকা কালেক্টরেট রেকর্ড রুম"
            },
            {
                "label": "এসএ সেটেলমেন্ট রেকর্ড",
                "ref": f"SA-KHATIAN-128-{p['dag_number']}",
                "status": "VERIFIED_ARCHIVE",
                "doc_type": "SA_KHATIAN",
                "doc_number": f"SA-KHATIAN-128-{p['dag_number']}",
                "registry_office": "সাভার উপজেলা ভূমি রেকর্ড রুম"
            },
            {
                "label": "রেজিস্ট্রি সাফ-কবালা বালাম",
                "ref": f"DEED-{deeds[0]['deed_number'] if deeds else '4215'}-VOL-42",
                "status": "REGISTERED",
                "doc_type": "SAF_KABALA_DEED",
                "doc_number": f"{deeds[0]['deed_number'] if deeds else 'SAVAR-2024-4215'}",
                "registry_office": "সাভার সাব-রেজিস্ট্রি অফিস"
            },
            {
                "label": "ই-নামজারি খারিজ আদেশ",
                "ref": f"MUT-CASE-{mutations[0]['case_number'] if mutations else '2017-0982'}",
                "status": "APPROVED_MUTATION",
                "doc_type": "E_MUTATION_DCR",
                "doc_number": f"{mutations[0]['case_number'] if mutations else 'SAVAR-MUT-2017-0982'}",
                "registry_office": "সহকারী কমিশনার (ভূমি) কার্যালয়, সাভার"
            }
        ],
        "disclaimer": "এই টাইমলাইনটি সরকারি বালাম বহি ও দলিলের ঐতিহাসিক রেকর্ডভিত্তিক চিত্র; এটি কোনো আইনি মালিকানার চূড়ান্ত ডিক্রি বা আদালতীয় ঘোষণা নয়।",
        "legal_disclaimer": "এই টাইমলাইনটি সরকারি বালাম বহি ও দলিলের ঐতিহাসিক রেকর্ডভিত্তিক চিত্র; এটি কোনো আইনি মালিকানার চূড়ান্ত ডিক্রি বা আদালতীয় ঘোষণা নয়।"
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
