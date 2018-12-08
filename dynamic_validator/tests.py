from django.test import TestCase

# Create your tests here.


class ModelFieldValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.data = [1, 3, 2]

    def test_equal(self):
        self.assertEqual(len(self.data), 3)
