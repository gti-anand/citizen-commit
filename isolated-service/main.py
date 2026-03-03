from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime

app = FastAPI(
    title="FastAPI Service",
    description="Glucose data service",
    version="1.0.0"
)

# Mock database
glucose_db = {}

class GlucoseReading(BaseModel):
    patient_id: str
    value: float
    unit: str = "mg/dL"

class GlucoseResponse(BaseModel):
    patient_id: str
    value: float
    unit: str
    timestamp: str
    status: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "fastapi-service", "version": "1.0.0"}

@app.post("/glucose", response_model=GlucoseResponse)
def add_reading(reading: GlucoseReading):
    timestamp = datetime.utcnow().isoformat()
    glucose_db[reading.patient_id] = {
        "value": reading.value,
        "unit": reading.unit,
        "timestamp": timestamp
    }
    return GlucoseResponse(
        patient_id=reading.patient_id,
        value=reading.value,
        unit=reading.unit,
        timestamp=timestamp,
        status="recorded"
    )

@app.get("/glucose/{patient_id}", response_model=GlucoseResponse)
def get_reading(patient_id: str):
    if patient_id not in glucose_db:
        raise HTTPException(status_code=404, detail="Patient not found")
    data = glucose_db[patient_id]
    return GlucoseResponse(
        patient_id=patient_id,
        value=data["value"],
        unit=data["unit"],
        timestamp=data["timestamp"],
        status="found"
    )