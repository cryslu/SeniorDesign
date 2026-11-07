import asyncio
import io
import unittest
import wave
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException
from fastapi import UploadFile
import numpy as np

import app


class QuestionApiTests(unittest.TestCase):
    def test_questions_endpoint_returns_question_bank(self):
        questions = app.questions()

        self.assertEqual(len(questions), 15)
        self.assertTrue(all(isinstance(question["id"], int) for question in questions))

    def test_audio_endpoint_resolves_integer_question_id(self):
        response = app.question_audio(1)

        self.assertTrue(str(response.path).endswith("/questions/audio/1.wav"))

    def test_score_uses_default_behavioral_rubric(self):
        expected_result = {"score": 75, "criteria": [], "feedback": []}
        request = app.EvaluateRequest(question_id=1, transcript="A practice answer.")

        with (
            patch.object(app, "evaluate", return_value=expected_result) as evaluate,
            patch.object(app, "summary", return_value="Practice feedback."),
        ):
            result = app.score(request)

        evaluate.assert_called_once_with(
            request.transcript, app.RUBRICS["R_BEHAVIOR"]
        )
        self.assertEqual(result["summary"], "Practice feedback.")

    def test_audio_endpoint_reports_unknown_question(self):
        with self.assertRaises(HTTPException) as error:
            app.question_audio(999)

        self.assertEqual(error.exception.status_code, 404)

    def test_transcribe_passes_pcm_samples_without_pyav_decoder(self):
        wav_data = io.BytesIO()
        with wave.open(wav_data, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(np.array([16384, -16384], dtype='<i2').tobytes())

        model = unittest.mock.Mock()
        model.transcribe.return_value = ([SimpleNamespace(text=' hello world ')], None)
        upload = UploadFile(filename='answer.wav', file=io.BytesIO(wav_data.getvalue()))

        with patch.object(app, 'get_whisper_model', return_value=model):
            result = asyncio.run(app.transcribe(upload))

        self.assertEqual(result, {'transcript': 'hello world'})
        samples = model.transcribe.call_args.args[0]
        self.assertIsInstance(samples, np.ndarray)
        np.testing.assert_allclose(samples, [0.5, -0.5])
        self.assertEqual(model.transcribe.call_args.kwargs['language'], 'en')

    def test_transcribe_rejects_invalid_wav(self):
        upload = UploadFile(filename='answer.wav', file=io.BytesIO(b'invalid'))

        with self.assertRaises(HTTPException) as error:
            asyncio.run(app.transcribe(upload))

        self.assertEqual(error.exception.status_code, 400)


if __name__ == "__main__":
    unittest.main()
