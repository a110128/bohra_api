from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware

from database import get_connection
from utils import validate_api_key
import config


# -----------------------------------------------------------
# FASTAPI APP INITIALIZATION
# -----------------------------------------------------------

app = FastAPI(
    title="Bohra Calendar API",
    version="1.0",
    description="Dawoodi Bohra fixed-tabular Hijri calendar with public and private endpoints."
)


# -----------------------------------------------------------
# CORS CONFIGURATION
# -----------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------
# PRIVATE AUTHENTICATION HELPERS
# -----------------------------------------------------------

def require_api_key(x_api_key: str = Header(None)):
    """
    Validates the API key for private endpoints.
    """
    if not validate_api_key(x_api_key, config.API_KEY):
        raise HTTPException(status_code=401, detail="Invalid or missing API Key")


# -----------------------------------------------------------
# PUBLIC ENDPOINTS
# -----------------------------------------------------------

@app.get(config.API_PREFIX + "/status")
def api_status():
    """
    API status check.
    """
    return {"status": "ok", "message": "Bohra Calendar API is running"}


@app.get(config.API_PREFIX + "/hijriToGregorian")
def hijri_to_gregorian(year: int, month: int, day: int):
    """
    Convert Hijri (AH) → Gregorian.
    """
    conn = get_connection()
    query = """
        SELECT gregorian
        FROM hijri_simple
        WHERE year = ? AND month = ? AND day = ?
    """
    row = conn.execute(query, (year, month, day)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "Hijri date not found")

    return {
        "hijri": f"{day}-{month}-{year} AH",
        "gregorian": row["gregorian"]
    }


@app.get(config.API_PREFIX + "/gregorianToHijri")
def gregorian_to_hijri(date: str):
    """
    Convert Gregorian → Hijri (AH).
    """
    conn = get_connection()
    query = """
        SELECT year, month, day
        FROM hijri_simple
        WHERE gregorian = ?
    """
    row = conn.execute(query, (date,)).fetchone()
    conn.close()

    if not row:
        raise HTTPException(404, "Gregorian date not found")

    return {
        "gregorian": date,
        "hijri": f"{row['day']}-{row['month']}-{row['year']} AH"
    }


@app.get(config.API_PREFIX + "/month")
def get_month(year: int, month: int):
    """
    Return full month calendar for a Hijri year/month.
    """
    conn = get_connection()
    query = """
        SELECT day, gregorian
        FROM hijri_simple
        WHERE year = ? AND month = ?
        ORDER BY day
    """
    rows = conn.execute(query, (year, month)).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(404, "Month not found")

    return {
        "year": year,
        "month": month,
        "days": [{"day": r["day"], "gregorian": r["gregorian"]} for r in rows]
    }


@app.get(config.API_PREFIX + "/year")
def get_year(year: int):
    """
    Return full year calendar.
    """
    conn = get_connection()
    query = """
        SELECT month, day, gregorian
        FROM hijri_simple
        WHERE year = ?
        ORDER BY month, day
    """
    rows = conn.execute(query, (year,)).fetchall()
    conn.close()

    if not rows:
        raise HTTPException(404, "Year not found")

    months = {}
    for r in rows:
        m = r["month"]
        if m not in months:
            months[m] = []
        months[m].append({"day": r["day"], "gregorian": r["gregorian"]})

    return {"year": year, "months": months}


# -----------------------------------------------------------
# PRIVATE ENDPOINTS (REQUIRE API KEY)
# -----------------------------------------------------------

@app.get(config.API_PREFIX + "/miqaat")
def get_miqaat(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    return {
        "miqaat": "Miqaat data will be added soon (private endpoint)."
    }


@app.get(config.API_PREFIX + "/device-sync")
def device_sync(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    return {"message": "Device sync OK"}


@app.get(config.API_PREFIX + "/firmware-update")
def firmware_update(x_api_key: str = Header(None)):
    require_api_key(x_api_key)
    return {"update": False}
