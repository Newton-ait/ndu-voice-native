"""FastAPI server for NDU Voice-Native"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from app.models import SpeakRequest, VoiceDesignRequest
from app.voice_engine import VoiceEngine
import io

app = FastAPI(title="NDU Voice-Native", version="1.0.0")
engine = VoiceEngine()
PIN = "ndu2026"

@app.get("/")
async def root():
    return {"service": "NDU Voice-Native", "voices": engine.list_voices()}

@app.post("/speak")
async def speak(request: SpeakRequest):
    if request.pin != PIN: raise HTTPException(401, "Invalid PIN")
    audio_bytes = await engine.speak(request.text, voice_name=request.voice, rate=request.rate, pitch=request.pitch)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mp3")

@app.post("/voice/clone")
async def clone_voice(audio: UploadFile = File(...), name: str = Form(...), pin: str = Form(...)):
    if pin != PIN: raise HTTPException(401, "Invalid PIN")
    profile = await engine.clone_voice(await audio.read(), name)
    return JSONResponse({"success": True, "voice": {"name": profile.name, "type": profile.voice_type}})

@app.post("/voice/design")
async def design_voice(request: VoiceDesignRequest):
    if request.pin != PIN: raise HTTPException(401, "Invalid PIN")
    profile = await engine.design_voice(request.description, request.name)
    return JSONResponse({"success": True, "voice": {"name": profile.name, "type": profile.voice_type}})

@app.get("/voices")
async def list_voices(pin: str):
    if pin != PIN: raise HTTPException(401, "Invalid PIN")
    return JSONResponse({"voices": engine.list_voices()})

@app.post("/conversation/speak")
async def conversation_speak(text: str = Form(...), voice: str = Form("jenny"), pin: str = Form(...)):
    if pin != PIN: raise HTTPException(401, "Invalid PIN")
    audio_bytes = await engine.speak(text, voice_name=voice)
    return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mp3")
