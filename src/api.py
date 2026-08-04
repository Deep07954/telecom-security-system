from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import our custom AI engine and simulator from Phase 4
from src.real_time_engine import ThreatDetectionEngine, TrafficSimulator

# 1. Initialize the FastAPI App
app = FastAPI(
    title="Telecom Security API",
    description="AI-Powered Threat Detection Engine for Telecom Networks",
    version="1.0.0"
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
# This allows our upcoming Streamlit frontend to talk to this backend securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend's IP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Load the AI Engine into memory when the server starts
print("[*] Starting API Server and loading ML models...")
engine = ThreatDetectionEngine()

# 4. Define the Data Schema using Pydantic
class TelecomEvent(BaseModel):
    session_duration: float
    packet_rate: float
    login_attempts: int
    location_switch_freq: int
    bandwidth_usage: float
    call_failures: int

# 5. Define API Endpoints

@app.get("/", tags=["Health"])
def health_check():
    """Check if the API is online."""
    return {"status": "Online", "message": "Telecom AI SOC Engine is active."}

@app.post("/api/v1/predict", tags=["Detection"])
def predict_threat(event: TelecomEvent):
    """
    Accepts a JSON payload of a telecom event, runs it through 
    the Random Forest and Isolation Forest, and returns a risk alert.
    """
    try:
        # Convert Pydantic model to a standard dictionary
        event_dict = event.model_dump()
        
        # Pass to our AI engine
        alert = engine.process_event(event_dict)
        return alert
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/simulate", tags=["Simulation"])
def simulate_event():
    """
    Triggers the internal simulator to generate a random network event 
    (with a 10% chance of attack) and immediately scores it.
    """
    try:
        live_event = TrafficSimulator.generate_event()
        alert = engine.process_event(live_event)
        return alert
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # This allows us to run the file directly for debugging
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)