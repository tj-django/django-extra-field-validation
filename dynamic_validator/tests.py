from django.contrib.auth import get_user_model
from django.test import TestCase

# Create your tests here.


class ModelFieldValidationTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.super_user = get_user_model().objects.create(username='super-test-user', is_superuser=True)
        cls.user = get_user_model().objects.create(username='test-user')

    def test_conditional_required_fields_raises_exception(self):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
            (
                lambda instance: instance.user.is_active, ['fixed_price', 'percentage', 'amount'],
            ),
        ]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)


    def test_required_fields_raises_exception(self):
        from demo.models import TestModel

        TestModel.REQUIRED_FIELDS = ['percentage']

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)


