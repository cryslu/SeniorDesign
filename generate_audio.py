import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
QUESTIONS_FILE = ROOT / "questions" / "questions.json"
AUDIO_DIR = ROOT / "questions" / "audio"

AUDIO_DIR.mkdir(parents=True, exist_ok=True)

with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
    questions = json.load(f)

for i, question in enumerate(questions):
    # Support question objects without an audio_file field
    question_id = str(question.get("id") or f"Q{i+1:03d}")

    # Support either "question" or "question_text"
    question_text = question.get("question") or question.get("question_text")

    if not question_text:
        print(f"Skipping {question_id}: no question text found")
        continue

    audio_filename = f"{question_id}.wav"
    output_path = AUDIO_DIR / audio_filename

    subprocess.run(
        [
            "espeak-ng",
            "-v", "en-us",
            "-s", "145",
            "-w", str(output_path),
            question_text
        ],
        check=True
    )

    # Store the audio filename in the question bank
    question["audio_file"] = f"audio/{audio_filename}"

    print(f"Generated: {output_path}")

with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=2, ensure_ascii=False)

print("Finished generating question audio!")
