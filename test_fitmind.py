import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import unittest
from backend.domain_detector import domain_detector
from backend.safety_service import safety_service
from backend.conversation_manager import conversation_manager
from backend.document_processor import document_processor
from backend.image_analyzer import validate_image
from backend.vector_store import vector_store

class TestFitMind(unittest.TestCase):

    def test_01_domain_detection_valid_queries(self):
        """Test health, workout, nutrition queries are accepted"""
        self.assertTrue(domain_detector.is_health_fitness_related("Create a beginner workout plan"))
        self.assertTrue(domain_detector.is_health_fitness_related("Suggest a healthy breakfast with high protein"))
        self.assertTrue(domain_detector.is_health_fitness_related("How many calories should I eat to lose weight?"))
        self.assertTrue(domain_detector.is_health_fitness_related("What are good yoga stretches for lower back pain?"))
        self.assertTrue(domain_detector.is_health_fitness_related("Hello!"))
        self.assertTrue(domain_detector.is_health_fitness_related("Thank you!"))

    def test_02_domain_detection_rejection(self):
        """Test unrelated queries (coding, politics, math, entertainment) are rejected"""
        self.assertFalse(domain_detector.is_health_fitness_related("Write a Python script to sort an array"))
        self.assertFalse(domain_detector.is_health_fitness_related("Who won the 2024 presidential election?"))
        self.assertFalse(domain_detector.is_health_fitness_related("Solve this calculus integral: x^2 dx"))
        self.assertFalse(domain_detector.is_health_fitness_related("What is the best movie on Netflix right now?"))
        self.assertFalse(domain_detector.is_health_fitness_related("Tell me about quantum physics"))

        # Check exact rejection message requirement
        expected_msg = (
            "I'm FitMind AI, your personal Health & Fitness Coach. "
            "I can help you with workouts, nutrition, healthy eating, fitness goals, "
            "weight management education, yoga, sleep and wellness. "
            "Please ask me something related to health and fitness!"
        )
        self.assertEqual(domain_detector.get_rejection_message().strip(), expected_msg.strip())

    def test_03_contextual_followups(self):
        """Test that short follow-up questions in health context are accepted"""
        history = [
            {"role": "user", "content": "Create a beginner workout plan for the gym."},
            {"role": "assistant", "content": "Here is a beginner gym workout routine: squats, bench press, lat pulldown."},
        ]
        # Follow-up should be accepted based on context
        self.assertTrue(domain_detector.is_health_fitness_related("Make it suitable for home", history))
        self.assertTrue(domain_detector.is_health_fitness_related("What about rest days?", history))
        self.assertTrue(domain_detector.is_health_fitness_related("Can you modify it?", history))

    def test_04_safety_service_emergency(self):
        """Test emergency symptoms trigger emergency response"""
        res = safety_service.check_emergency("I have severe chest pain and can't breathe")
        self.assertIsNotNone(res)
        self.assertIn("medical emergency", res)
        self.assertIn("call your local emergency number", res)

    def test_05_safety_service_diagnosis(self):
        """Test medical diagnosis requests are flagged"""
        self.assertTrue(safety_service.check_medical_diagnosis("Can you diagnose me? I have a strange rash"))
        self.assertTrue(safety_service.check_medical_diagnosis("What disease do I have?"))
        self.assertTrue(safety_service.check_medical_diagnosis("What medicine should you prescribe me?"))

    def test_06_conversation_manager(self):
        """Test creating, reading, updating, and isolating conversations"""
        conv1 = conversation_manager.create_conversation("Workout Plan Session")
        conv2 = conversation_manager.create_conversation("Diet Plan Session")
        self.assertNotEqual(conv1["id"], conv2["id"])

        conversation_manager.add_message(conv1["id"], "user", "Hello workout")
        conversation_manager.add_message(conv1["id"], "assistant", "Here is your workout")

        conversation_manager.add_message(conv2["id"], "user", "Hello diet")
        conversation_manager.add_message(conv2["id"], "assistant", "Here is your diet")

        # Verify isolation
        history1 = conversation_manager.get_conversation_history(conv1["id"])
        history2 = conversation_manager.get_conversation_history(conv2["id"])

        self.assertEqual(len(history1), 2)
        self.assertEqual(len(history2), 2)
        self.assertIn("workout", history1[0]["content"])
        self.assertIn("diet", history2[0]["content"])

        # Clean up test convs
        conversation_manager.delete_conversation(conv1["id"])
        conversation_manager.delete_conversation(conv2["id"])

    def test_07_document_validation(self):
        """Test document validation for supported and unsupported formats"""
        valid_pdf, _ = document_processor.validate_document(b"%PDF-1.4 test", "application/pdf", "workout.pdf")
        self.assertTrue(valid_pdf)

        valid_docx, _ = document_processor.validate_document(b"PK test", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "diet.docx")
        self.assertTrue(valid_docx)

        valid_txt, _ = document_processor.validate_document(b"Healthy habits text", "text/plain", "habits.txt")
        self.assertTrue(valid_txt)

        # Unsupported format (exe, mp3, etc.)
        invalid, err = document_processor.validate_document(b"fake binary", "application/octet-stream", "virus.exe")
        self.assertFalse(invalid)
        self.assertIn("Unsupported file format", err)

    def test_08_image_validation(self):
        """Test image validation"""
        # Invalid mime type
        invalid, err = validate_image(b"fake data", "application/pdf")
        self.assertFalse(invalid)

    def test_09_vector_store_retrieval(self):
        """Test vector store indexing and semantic search"""
        chunks = [
            {"text": "Cardio exercises improve cardiovascular health and boost stamina through running, cycling, and swimming.", "page": "1", "source": "Page 1"},
            {"text": "Protein is essential for muscle hypertrophy. Target 1.6 to 2.2 grams per kg of bodyweight daily.", "page": "2", "source": "Page 2"},
            {"text": "Hydration helps joint lubrication and nutrient transport. Drink adequate fluids throughout workouts.", "page": "3", "source": "Page 3"},
        ]
        index_id = "test_index_123"
        success = vector_store.create_index(index_id, chunks)
        self.assertTrue(success)

        # Search for muscle hypertrophy
        results = vector_store.search(index_id, "How much protein do I need for muscle growth?", top_k=1)
        self.assertGreater(len(results), 0)
        self.assertIn("Protein", results[0]["text"])

        # Search for cardio
        results_cardio = vector_store.search(index_id, "running and stamina", top_k=1)
        self.assertGreater(len(results_cardio), 0)
        self.assertIn("Cardio", results_cardio[0]["text"])

        # Clean up
        vector_store.delete_index(index_id)

if __name__ == "__main__":
    unittest.main()
