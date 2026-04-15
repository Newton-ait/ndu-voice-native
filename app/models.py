"""Pydantic models for NDU Voice-Native"""
from pydantic import BaseModel
from typing import Optional, Literal

class SpeakRequest(BaseModel):
    text: str
    voice: str = "jenny"
    rate: str = "+5%"
    pitch: str = "+2Hz"
    pin: str

class VoiceDesignRequest(BaseModel):
    name: str
    description: str
    pin: str

class VoiceProfile(BaseModel):
    name: str
    voice_type: Literal["preset", "cloned", "designed"]
    description: Optional[str] = None
    edge_tts_voice: Optional[str] = None
    rate: str = "+5%"
    pitch: str = "+2Hz"
