import unittest
from rag_cag import RAGCAG

class RAGCAGTest(unittest.TestCase):
    def setUp(self):
        self.ragcag = RAGCAG()

    def test_retrieve_knowledge(self):
        results = self.ragcag.retrieve_knowledge("test query")
        self.assertIsNotNone(results)

    def test_augment_response(self):
        response = self.ragcag.augment_response("test query", "test context")
        self.assertIsNotNone(response)

if __name__ == '__main__':
    unittest.main()
