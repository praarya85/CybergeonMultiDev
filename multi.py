import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from google import genai
from google.genai import types

# --- 1. CONFIGURATION ---
API_KEY = "AIzaSyA8vWlatyC8U-HVlhDeALMRDvspLrcrslI"
client = genai.(api_key=API_KEY)

# Using the latest 2026 production models
REASONING_MODEL = "gemini-3.1-pro"        # For deep logic extraction
PRODUCTION_MODEL = "gemini-3.1-flash-lite" # Optimized for speed/cost in code generation

app = FastAPI(title="Ghost-Dev v2 (Gemini 3.1)")

class GhostDevEngine:
    def __init__(self, client):
        self.client = client

    def run_archaeologist(self, legacy_content: str) -> str:
        """Agent 1: Deep logic extraction using Gemini 3.1 Pro."""
        instruction = (
            "You are a Senior Software Archaeologist using Gemini 3.1 Pro. "
            "Analyze the legacy code for complex business intent and 'Sober' logic."
        )
        # 3.1 Pro handles complex reasoning significantly better than the 1.5 series
        response = self.client.models.generate_content(
            model=REASONING_MODEL,
            config=types.GenerateContentConfig(system_instruction=instruction),
            contents=legacy_content
        )
        return response.text

    def run_ghost_writer(self, tech_spec: str) -> str:
        """Agent 2: Fast code generation using Gemini 3.1 Flash-Lite."""
        instruction = (
            "You are a Lead Python Developer using Gemini 3.1 Flash-Lite. "
            "Generate minimalist, high-performance FastAPI code based on the spec."
        )
        # Flash-Lite is 60% more cost-effective for large token outputs
        response = self.client.models.generate_content(
            model=PRODUCTION_MODEL,
            config=types.GenerateContentConfig(system_instruction=instruction),
            contents=tech_spec
        )
        return response.text

# --- 2. THE PIPELINE ---
@app.post("/modernize")
async def modernize(file: UploadFile = File(...)):
    content = await file.read()
    legacy_code = content.decode("utf-8")
    
    # Sequential processing
    blueprint = engine.run_archaeologist(legacy_code)
    modern_code = engine.run_ghost_writer(blueprint)
    
    return {
        "engine": "Gemini 3.1 Pipeline",
        "modern_code": modern_code
    }

if __name__ == "__main__":
    engine = GhostDevEngine(client)
    uvicorn.run(app, host="0.0.0.0", port=8000)
