"""
AI Content Pipeline — FastAPI Backend
Draait op Hetzner server, stuurt pipeline aan via HTTP endpoints
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import subprocess
import threading
import json
import urllib.request
import urllib.error
import os
from datetime import datetime
from typing import Optional

app = FastAPI(title="AI Content Pipeline API")

# CORS — zodat de HTML pagina verbinding kan maken
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CONFIGURATIE
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://txuzmuhbmvzqotjuffhv.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR4dXptdWhibXZ6cW90anVmZmh2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzcwNDMzMTMsImV4cCI6MjA5MjYxOTMxM30.irLNWt6YIN39bOqCiEosBiXJU5jsycG91d0OX3tRVgg")
PIPELINE_DIR = "/opt/ai-content-pipeline"

# Pipeline status bijhouden
pipeline_status = {
    "draait": False,
    "huidige_agent": None,
    "logs": [],
    "laatste_run": None,
    "product": None
}

# ============================================================
# SUPABASE HELPER
# ============================================================

def supabase_get(tabel, filter=""):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/{tabel}?{filter}",
        method="GET"
    )
    req.add_header("apikey", SUPABASE_KEY)
    req.add_header("Authorization", f"Bearer {SUPABASE_KEY}")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except:
        return []

# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
def root():
    return {"status": "AI Content Pipeline API draait", "versie": "1.0"}

@app.get("/status")
def get_status():
    """Huidige pipeline status ophalen"""
    return {
        "draait":        pipeline_status["draait"],
        "huidige_agent": pipeline_status["huidige_agent"],
        "laatste_run":   pipeline_status["laatste_run"],
        "product":       pipeline_status["product"],
        "logs":          pipeline_status["logs"][-50:]  # Laatste 50 logs
    }

@app.get("/producten")
def get_producten():
    """Alle actieve producten ophalen uit Supabase"""
    data = supabase_get("producten", "select=id,product_naam,status,categorie,primaire_kleur,soul_hex_kleuren,moodboard_status,research_gedaan,product_image_url&status=eq.Actief&order=id.desc")
    return {"producten": data}

@app.get("/pipeline-runs")
def get_pipeline_runs():
    """Laatste pipeline runs ophalen"""
    data = supabase_get("pipeline_runs", "select=*&order=aangemaakt_op.desc&limit=10")
    return {"runs": data}

@app.get("/publicaties")
def get_publicaties():
    """Laatste publicaties ophalen"""
    data = supabase_get("publicaties", "select=*&order=aangemaakt_op.desc&limit=20")
    return {"publicaties": data}

@app.post("/pipeline/starten")
def start_pipeline(background_tasks: BackgroundTasks):
    """Start de volledige dagelijkse pipeline"""
    if pipeline_status["draait"]:
        return {"success": False, "bericht": "Pipeline draait al"}

    background_tasks.add_task(run_pipeline)
    return {"success": True, "bericht": "Pipeline gestart"}

@app.post("/pipeline/stoppen")
def stop_pipeline():
    """Stop de pipeline"""
    pipeline_status["draait"] = False
    pipeline_status["huidige_agent"] = None
    log_toevoegen("Pipeline gestopt door gebruiker", "amber")
    return {"success": True, "bericht": "Pipeline gestopt"}

class NieuwProductData(BaseModel):
    product_naam: str
    product_url: Optional[str] = ""
    doelland: Optional[str] = "Nederland"
    doeltaal: Optional[str] = "Nederlands"

@app.post("/product/nieuw")
def nieuw_product(data: NieuwProductData):
    """Registreer een nieuw product — start Agent 0 interview via pipeline"""
    log_toevoegen(f"Nieuw product aangemeld: {data.product_naam}", "gold")
    return {
        "success": True,
        "bericht": f"Product {data.product_naam} aangemeld. Start het interview via de pipeline.",
        "instructie": f"Voer uit op server: python3 {PIPELINE_DIR}/volledige_pipeline.py --interview"
    }

@app.get("/logs")
def get_logs():
    """Laatste logs ophalen"""
    return {"logs": pipeline_status["logs"][-100:]}

@app.delete("/logs")
def clear_logs():
    """Logs wissen"""
    pipeline_status["logs"] = []
    return {"success": True}

# ============================================================
# PIPELINE RUNNER
# ============================================================

def log_toevoegen(tekst, type="dim"):
    tijdstip = datetime.now().strftime("%H:%M:%S")
    pipeline_status["logs"].append({
        "tijd":  tijdstip,
        "tekst": tekst,
        "type":  type
    })
    # Maximaal 500 logs bewaren
    if len(pipeline_status["logs"]) > 500:
        pipeline_status["logs"] = pipeline_status["logs"][-500:]


def run_pipeline():
    """Voert de pipeline uit als background task"""
    pipeline_status["draait"]     = True
    pipeline_status["laatste_run"] = datetime.now().strftime("%d-%m-%Y %H:%M")
    pipeline_status["logs"]       = []

    log_toevoegen("Pipeline gestart", "gold")
    log_toevoegen(f"Tijdstip: {datetime.now().strftime('%d-%m-%Y %H:%M')}", "dim")

    try:
        process = subprocess.Popen(
            ["python3", f"{PIPELINE_DIR}/volledige_pipeline.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=PIPELINE_DIR
        )

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            # Bepaal log type op basis van inhoud
            if "✓" in line or "succesvol" in line.lower() or "klaar" in line.lower():
                type = "green"
            elif "fout" in line.lower() or "error" in line.lower() or "mislukt" in line.lower():
                type = "red"
            elif "[Agent" in line:
                type = "amber"
            elif "Pipeline" in line:
                type = "gold"
            else:
                type = "dim"

            log_toevoegen(line, type)

            # Huidige agent bijhouden
            for agent_num in ["0", "2", "3", "4", "5", "6"]:
                if f"[Agent {agent_num}]" in line:
                    pipeline_status["huidige_agent"] = int(agent_num)

        process.wait()
        log_toevoegen("Pipeline voltooid", "green")

    except Exception as e:
        log_toevoegen(f"Pipeline fout: {str(e)}", "red")

    finally:
        pipeline_status["draait"]     = False
        pipeline_status["huidige_agent"] = None


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
