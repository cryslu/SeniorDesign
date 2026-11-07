import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BehavioralQuestionsStructureTests(unittest.TestCase):
    def test_behavioral_questions_structure(self):
        questions = json.loads(
            (ROOT / "questions" / "questions.json").read_text()
        )

        self.assertTrue(questions)
        self.assertEqual(len(questions), len({question["id"] for question in questions}))

        for question in questions:
            with self.subTest(question_id=question["id"]):
                self.assertIsInstance(question["id"], int)
                self.assertTrue(question["category"])
                self.assertTrue(question["competency"])
                self.assertTrue(question["question"])
                self.assertIn(question["difficulty"], {"easy", "medium", "hard"})
                self.assertTrue(question["follow_ups"])
                self.assertTrue(question["evaluation_criteria"])
                self.assertTrue(
                    (ROOT / "questions" / question["audio_file"]).is_file()
                )
