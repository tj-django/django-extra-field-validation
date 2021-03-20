from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class FieldValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.super_user = User.objects.create(
            username="super-test-user", is_superuser=True
        )
        cls.user = User.objects.create(username="test-user")

    def test_conditional_required_field_raises_exception_when_missing(self):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_FIELDS = [
            (
                lambda instance: instance.user.is_active,
                ["percentage"],
            ),
        ]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)

    def test_conditional_required_field_is_valid(self):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_FIELDS = [
            (
                lambda instance: instance.user.is_active,
                ["percentage"],
            ),
        ]

        TestModel.objects.create(user=self.user, percentage=25)

    def test_conditional_required_toggle_field_raises_exception_when_missing(self):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
            (
                lambda instance: instance.user.is_active,
                ["fixed_price", "percentage", "amount"],
            ),
        ]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)

    def test_conditional_required_toggle_field_raises_exception_with_2_fields(
        self,
    ):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
            (
                lambda instance: instance.user.is_active,
                ["fixed_price", "percentage", "amount"],
            ),
        ]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user, percentage=25, fixed_price=10)

    def test_conditional_required_toggle_field_is_valid(self):
        from demo.models import TestModel

        TestModel.CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
            (
                lambda instance: instance.user.is_active,
                ["fixed_price", "percentage", "amount"],
            ),
        ]

        TestModel.objects.create(user=self.user, percentage=25)

    def test_required_fields_raises_exception(self):
        from demo.models import TestModel

        TestModel.REQUIRED_FIELDS = ["percentage"]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)

    def test_providing_a_required_field_saves_the_instance(self):
        from demo.models import TestModel

        TestModel.REQUIRED_FIELDS = ["percentage"]

        obj = TestModel.objects.create(user=self.user, percentage=25)

        self.assertEqual(obj.percentage, 25)

    def test_providing_more_than_one_required_field_raises_an_error(self):
        from demo.models import TestModel

        TestModel.REQUIRED_FIELDS = ["percentage", "fixed_price"]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user, percentage=25, fixed_price=10)

    def test_optional_required_fields_is_valid(self):
        from demo.models import TestModel

        TestModel.REQUIRED_TOGGLE_FIELDS = ["fixed_price", "percentage", "amount"]

        TestModel.objects.create(user=self.user, percentage=25)

    def test_optional_required_fields_raised_exception_when_invalid(self):
        from demo.models import TestModel

        TestModel.REQUIRED_TOGGLE_FIELDS = ["fixed_price", "percentage", "amount"]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user)
            TestModel.objects.create(user=self.user, percentage=25, amount=25)
            TestModel.objects.create(user=self.user, fixed_price=25, amount=25)

    def test_optional_toggle_fields_is_valid(self):
        from demo.models import TestModel

        TestModel.OPTIONAL_TOGGLE_FIELDS = ["fixed_price", "percentage", "amount"]

        TestModel.objects.create(user=self.user, percentage=25)

    def test_optional_toggle_fields_raised_exception_when_invalid(self):
        from demo.models import TestModel

        TestModel.OPTIONAL_TOGGLE_FIELDS = ["fixed_price", "percentage", "amount"]

        with self.assertRaises(ValueError):
            TestModel.objects.create(user=self.user, percentage=25, amount=25)
            TestModel.objects.create(user=self.user, fixed_price=25, amount=25)
