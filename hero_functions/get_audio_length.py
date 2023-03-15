from mutagen.mp3 import MP3
from mutagen.oggvorbis import OggVorbis

def get_audio_length(path: str):
    if path.endswith(".mp3"):
        return MP3(path).info.length

    if path.endswith(".ogg"):
        return OggVorbis(path).info.length
    
    raise Exception(f"Unknown audio type {path}")

