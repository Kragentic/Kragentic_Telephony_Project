import unittest
from ai_agent import AIAgent

class AIAgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = AIAgent()

    def test_process_input(self):
        response = self.agent.process_input("Hello, world!")
        self.assertIsNotNone(response)

    def test_generate_response(self):
        response = self.agent.generate_response("Hello, world!")
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
