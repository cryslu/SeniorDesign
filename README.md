# Offline Interview Practice — CPU-only MVP

Features: categorized behavioral question bank, prerecorded spoken questions, 2-minute microphone recording, local Whisper (faster-whisper) transcription, editable transcript, MiniLM sentence embedding rubric scoring, template-based feedback. No cloud API, no GPU, no database, no user transcript persistence.

## Setup (development machine with internet)

Requires Python 3.10+ and a working microphone. Run from the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup_models.py
```

The setup script downloads the **Whisper tiny.en** model in faster-whisper/CTranslate2 format into `models/whisper-tiny-en/`, alongside MiniLM. Both run on CPU without an API or GPU. For prerecorded question audio, install `espeak-ng` (`brew install espeak-ng` on macOS, or `sudo apt install espeak-ng` on Ubuntu), then run:

```bash
python generate_audio.py
uvicorn app:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 . Microphone access works on localhost in modern browsers. Once installed, **disconnect internet and test again**. On a separate offline machine, copy the complete project including the downloaded `models/` folder, Python dependencies (install from offline wheels), and generated `questions/audio/` WAV files. `setup_models.py` must never run on the offline device.

## Important deployment limits

- This is a **local Python server + browser** prototype, not a standalone Android tablet app. On locked-down tablets that cannot run Python or install model files, port inference to supported native/mobile runtimes or use an approved facility-local server.
- Question audio is pre-generated, not live cloud TTS.
- No responses are saved by default. `transcripts/` is reserved for **consented test fixtures only**, never real users' data in Git.
- Scores are unvalidated similarity-derived practice indicators. Similarity cannot reliably assess truthfulness, safety, negation, or real interview performance. Have qualified humans validate rubric content, fairness, calibration, and technical safety before deployment. In particular, safety-critical construction/CDL responses must not be certified using embeddings alone.
- `ScriptProcessorNode` is used for simplicity in this MVP; production should use AudioWorklet. WAV recording stays in browser memory until uploaded to localhost. This demo is not hardened for multi-user or shared-device use.
- Model licenses and facility policies must be checked before deployment.

## Tests

```bash
python -m unittest discover -s tests -v
```
