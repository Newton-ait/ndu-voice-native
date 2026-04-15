"""Voice Engine with TTS, cloning, and design"""
import os, json, io, tempfile
import torch, torchaudio
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class VoiceProfile:
    name: str
    voice_type: Literal["preset", "cloned", "designed"]
    edge_tts_voice: Optional[str] = None
    reference_path: Optional[str] = None
    description: Optional[str] = None
    rate: str = "+5%"
    pitch: str = "+2Hz"

class VoiceEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.omnivoice = None
        self.profiles = {
            "jenny": VoiceProfile(name="Jenny", voice_type="preset", edge_tts_voice="en-US-JennyNeural", description="Bright, friendly"),
            "emma": VoiceProfile(name="Emma", voice_type="preset", edge_tts_voice="en-US-EmmaMultilingualNeural", description="Warm, natural"),
            "ryan": VoiceProfile(name="Ryan", voice_type="preset", edge_tts_voice="en-GB-RyanNeural", description="British, smooth"),
            "aria": VoiceProfile(name="Aria", voice_type="preset", edge_tts_voice="en-US-AriaNeural", description="Clear, confident"),
            "sonia": VoiceProfile(name="Sonia", voice_type="preset", edge_tts_voice="en-GB-SoniaNeural", description="Cheerful, engaging")
        }
    
    async def speak(self, text: str, voice_name: str = "jenny", **kwargs) -> bytes:
        profile = self.profiles.get(voice_name, self.profiles["jenny"])
        if "rate" in kwargs: profile.rate = kwargs["rate"]
        if "pitch" in kwargs: profile.pitch = kwargs["pitch"]
        
        if profile.voice_type == "preset":
            import edge_tts
            communicate = edge_tts.Communicate(text, profile.edge_tts_voice, rate=profile.rate, pitch=profile.pitch)
            audio_data = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
            return audio_data.getvalue()
        elif profile.voice_type == "cloned":
            if not self.omnivoice:
                from omnivoice import OmniVoice
                self.omnivoice = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=self.device)
            audio = self.omnivoice.generate(text=text, ref_audio=profile.reference_path)
            buffer = io.BytesIO()
            torchaudio.save(buffer, audio[0].cpu(), 24000, format="wav")
            return buffer.getvalue()
        elif profile.voice_type == "designed":
            if not self.omnivoice:
                from omnivoice import OmniVoice
                self.omnivoice = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=self.device)
            audio = self.omnivoice.generate(text=text, instruct=profile.description)
            buffer = io.BytesIO()
            torchaudio.save(buffer, audio[0].cpu(), 24000, format="wav")
            return buffer.getvalue()
    
    async def clone_voice(self, audio_bytes: bytes, name: str) -> VoiceProfile:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            ref_path = f.name
        profile = VoiceProfile(name=name, voice_type="cloned", reference_path=ref_path, description=f"Custom: {name}")
        self.profiles[name] = profile
        return profile
    
    async def design_voice(self, description: str, name: str) -> VoiceProfile:
        profile = VoiceProfile(name=name, voice_type="designed", description=description)
        self.profiles[name] = profile
        return profile
    
    def list_voices(self) -> list:
        return [{"name": n, "type": p.voice_type, "description": p.description} for n, p in self.profiles.items()]
