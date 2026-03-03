from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="Glucode Service",
    description="Microservice that consumes fastapi-service",
    version="1.0.0"
)

FASTAPI_SERVICE_URL = "http://localhost:8000"

class ReadingRequest(BaseModel):
    patient_id: str
    value: float
    unit: str = "mg/dL"

class AnalysisResponse(BaseModel):
    patient_id: str
    value: float
    unit: str
    timestamp: str
    risk_level: str
    message: str

def analyze_glucose(value: float) -> tuple[str, str]:
    if value < 70:
        return "HIGH RISK", "⚠️ Hypoglycemia detected"
    elif value <= 140:
        return "NORMAL", "✅ Glucose level is normal"
    elif value <= 200:
        return "MODERATE RISK", "⚠️ Elevated glucose level"
    else:
        return "HIGH RISK", "🚨 Hyperglycemia detected"

@app.get("/health")
def health():
    return {"status": "ok", "service": "glucode-service", "version": "1.0.0"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze(request: ReadingRequest):
    # Send reading to fastapi-service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{FASTAPI_SERVICE_URL}/glucose",
                json=request.model_dump(),
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="fastapi-service unreachable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))

    risk_level, message = analyze_glucose(request.value)

    return AnalysisResponse(
        patient_id=data["patient_id"],
        value=data["value"],
        unit=data["unit"],
        timestamp=data["timestamp"],
        risk_level=risk_level,
        message=message
    )

@app.get("/analyze/{patient_id}", response_model=AnalysisResponse)
async def get_analysis(patient_id: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{FASTAPI_SERVICE_URL}/glucose/{patient_id}",
                timeout=5.0
            )
            response.raise_for_status()
            data = response.json()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="fastapi-service unreachable")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=str(e))

    risk_level, message = analyze_glucose(data["value"])

    return AnalysisResponse(
        patient_id=data["patient_id"],
        value=data["value"],
        unit=data["unit"],
        timestamp=data["timestamp"],
        risk_level=risk_level,
        message=message
    )