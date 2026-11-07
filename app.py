from pathlib import Path
import io
import json
import wave
from functools import lru_cache
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import numpy as np
from pydantic import BaseModel
from scoring.evaluate import evaluate
from scoring.feedback import summary
ROOT=Path(__file__).resolve().parent
QUESTIONS=json.loads((ROOT/'questions/questions.json').read_text())
RUBRICS=json.loads((ROOT/'rubrics/rubrics.json').read_text())
app=FastAPI(title='Offline Interview Practice')
app.mount('/static',StaticFiles(directory=str(ROOT/'frontend')),name='static')

@app.get('/')
def home(): return FileResponse(ROOT/'frontend/index.html')

@app.get('/api/questions')
def questions(): return QUESTIONS

@app.get('/api/questions/{qid}/audio')
def question_audio(qid:int):
    q=next((x for x in QUESTIONS if x['id']==qid),None)
    if not q: raise HTTPException(404,'Question not found')
    audio=ROOT/'questions'/q['audio_file']
    if not audio.is_file(): raise HTTPException(404,'Question audio not generated; run generate_audio.py')
    return FileResponse(audio,media_type='audio/wav')

class EvaluateRequest(BaseModel):
    question_id:int
    transcript:str

@app.post('/api/evaluate')
def score(req:EvaluateRequest):
    q=next((x for x in QUESTIONS if x['id']==req.question_id),None)
    if not q: raise HTTPException(404,'Question not found')
    if len(req.transcript)>20000: raise HTTPException(413,'Transcript too long')
    rubric_id=q.get('rubric_id','R_BEHAVIOR')
    if rubric_id not in RUBRICS:
        raise HTTPException(500,f'Rubric {rubric_id} is not configured')
    result=evaluate(req.transcript,RUBRICS[rubric_id]); result['summary']=summary(result)
    return result

@lru_cache(maxsize=1)
def get_whisper_model():
    from faster_whisper import WhisperModel
    model_path = ROOT / 'models' / 'whisper-tiny-en'
    if not model_path.is_dir():
        raise HTTPException(503, 'Offline Whisper model missing; run setup_models.py on a connected development computer')
    return WhisperModel(str(model_path), device='cpu', compute_type='int8', local_files_only=True)

@app.post('/api/transcribe')
async def transcribe(audio: UploadFile = File(...)):
    """Transcribe 16 kHz mono PCM WAV locally with CPU-only Whisper."""
    data = await audio.read(12 * 1024 * 1024 + 1)
    if len(data) > 12 * 1024 * 1024:
        raise HTTPException(413, 'Audio too large')
    try:
        with wave.open(io.BytesIO(data), 'rb') as wf:
            if (wf.getnchannels(), wf.getsampwidth(), wf.getcomptype(), wf.getframerate()) != (1, 2, 'NONE', 16000):
                raise HTTPException(400, 'Expected mono 16-bit PCM WAV at 16kHz')
            frame_count = wf.getnframes()
            if frame_count > 16000 * 125:
                raise HTTPException(413, 'Recording exceeds the 2-minute limit')
            pcm_data = wf.readframes(frame_count)
            if len(pcm_data) != frame_count * 2:
                raise HTTPException(400, 'Invalid WAV file')
    except (wave.Error, EOFError):
        raise HTTPException(400, 'Invalid WAV file')
    if not pcm_data:
        return {'transcript': ''}
    samples = np.frombuffer(pcm_data, dtype='<i2').astype(np.float32) / 32768.0
    model = get_whisper_model()
    segments, _ = model.transcribe(samples, language='en', beam_size=1, vad_filter=True, condition_on_previous_text=False)
    return {'transcript': ' '.join(segment.text.strip() for segment in segments).strip()}
