from contextlib import asynccontextmanager
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ml_service import get_demo_assessment

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
DB_PATH = Path(__file__).resolve().parent / "readings.db"


def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                heart_rate REAL,
                spo2 REAL,
                skin_temperature REAL,
                pulse_feature REAL,
                motion_detected INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL DEFAULT 'demo'
            )
        """)
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Anemia Awareness Glove API",
    description=(
        "Educational wearable prototype API. This application does not diagnose "
        "anemia or detect blood loss."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# The frontend is served by this same FastAPI server, so CORS is not normally
# needed. It is enabled here to make later development from a separate frontend
# server easier.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For a local student demo only; restrict before deployment.
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ReadingIn(BaseModel):
    heart_rate: Optional[float] = Field(default=None, ge=0, le=250)
    spo2: Optional[float] = Field(default=None, ge=0, le=100)
    skin_temperature: Optional[float] = Field(default=None, ge=0, le=60)
    pulse_feature: Optional[float] = Field(default=None, ge=0, le=1)
    motion_detected: bool = False
    source: str = Field(default="esp32", max_length=30)


def row_to_dict(row):
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "heart_rate": row["heart_rate"],
        "spo2": row["spo2"],
        "skin_temperature": row["skin_temperature"],
        "pulse_feature": row["pulse_feature"],
        "motion_detected": bool(row["motion_detected"]),
        "source": row["source"],
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/api/readings")
def create_reading(reading: ReadingIn):
    # At least one real measurement must be provided.
    if all(value is None for value in [
        reading.heart_rate, reading.spo2,
        reading.skin_temperature, reading.pulse_feature
    ]):
        raise HTTPException(
            status_code=400,
            detail="Send at least one sensor measurement."
        )

    timestamp = datetime.now(timezone.utc).isoformat()
    with connect_db() as db:
        cursor = db.execute(
            """
            INSERT INTO readings
            (created_at, heart_rate, spo2, skin_temperature,
             pulse_feature, motion_detected, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                timestamp, reading.heart_rate, reading.spo2,
                reading.skin_temperature, reading.pulse_feature,
                int(reading.motion_detected), reading.source
            ),
        )
        db.commit()
        saved = db.execute(
            "SELECT * FROM readings WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()

    return {"message": "Reading saved", "reading": row_to_dict(saved)}


@app.get("/api/readings/latest")
def latest_reading():
    with connect_db() as db:
        row = db.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return {"reading": None}
    return {"reading": row_to_dict(row)}


@app.get("/api/readings/history")
def readings_history(limit: int = 30):
    if limit < 1 or limit > 500:
        raise HTTPException(status_code=400, detail="limit must be from 1 to 500")
    with connect_db() as db:
        rows = db.execute(
            "SELECT * FROM readings ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    # Return oldest-to-newest for graphs.
    return {"readings": [row_to_dict(row) for row in reversed(rows)]}


@app.delete("/api/readings")
def delete_readings():
    # Demo convenience endpoint. Do not expose an unauthenticated delete endpoint
    # in a public deployment.
    with connect_db() as db:
        db.execute("DELETE FROM readings")
        db.commit()
    return {"message": "All demo readings deleted"}


@app.post("/api/predict")
def predict():
    """
    Placeholder integration point for the teammate's ML model.
    This is intentionally NOT a medical prediction.
    Replace ml_service.py only after agreeing on model inputs/outputs with
    the ML teammate and validating the model.
    """
    latest = latest_reading()["reading"]
    if latest is None:
        raise HTTPException(
            status_code=400,
            detail="No readings available. Send or generate a reading first."
        )
    return get_demo_assessment(latest)


@app.get("/")
def homepage():
    return FileResponse(FRONTEND_DIR / "index.html")


# Serve CSS, JavaScript, and any other frontend files.
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
