django-extra-field-validation
===============================

![PyPI](https://img.shields.io/pypi/v/django-extra-field-validation) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-extra-field-validation) ![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-extra-field-validation) [![Downloads](https://pepy.tech/badge/django-extra-field-validation)](https://pepy.tech/project/django-extra-field-validation)

[![CI Test](https://github.com/tj-django/django-extra-field-validation/actions/workflows/test.yml/badge.svg)](https://github.com/tj-django/django-extra-field-validation/actions/workflows/test.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/6973bc063f1142afb66d897261d8f8f5)](https://www.codacy.com/gh/tj-django/django-extra-field-validation/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tj-django/django-extra-field-validation&amp;utm_campaign=Badge_Grade) [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/6973bc063f1142afb66d897261d8f8f5)](https://www.codacy.com/gh/tj-django/django-extra-field-validation/dashboard?utm_source=github.com&utm_medium=referral&utm_content=tj-django/django-extra-field-validation&utm_campaign=Badge_Coverage)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/tj-django/django-extra-field-validation.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-extra-field-validation/alerts/) [![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/tj-django/django-extra-field-validation.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/tj-django/django-extra-field-validation/context:python)

Introduction
------------
This package aims to provide tools needed to define custom field validation logic which can be used independently or with
django forms, test cases, API implementation or any model operation that requires saving data to the database.

This can also be extended by defining table check constraints if needed but currently validation
will only be handled at the model level.


Installation
------------

```shell script
pip install django-extra-field-validation
```

Usage
-----
This provides model level validation which includes:

  - [Required field validation](#require-a-single-field-in-a-collection)
  - [Optional field validation](#optionally-required-fields)
  - [Conditional field validation](#conditional-required-fields)

### Require a single field in a collection

```py

from django.db import models
from extra_validator import FieldValidationMixin


class TestModel(FieldValidationMixin, models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    REQUIRED_TOGGLE_FIELDS = [
        ['amount', 'fixed_price', 'percentage'],  # Require only one of the following fields.
    ]

```

Example

```python
In [1]: from decimal import Decimal

In [2]: from demo.models import TestModel

In [3]: TestModel.objects.create(amount=Decimal('2.50'), fixed_price=Decimal('3.00'))
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {'fixed_price': ValidationError([u'Please provide only one of: Amount, Fixed price, Percentage'])}

```

### Require all fields

```py

from django.db import models
from extra_validator import FieldValidationMixin


class TestModel(FieldValidationMixin, models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    REQUIRED_FIELDS = ['amount']  # Always requires an amount to create the instance.
```

Example

```python
In [1]: from decimal import Decimal

In [2]: from demo.models import TestModel

In [3]: TestModel.objects.create(fixed_price=Decimal('3.00'))
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {'amount': ValidationError([u'Please provide a value for: "amount".'])}

```

### Optionally required fields

```py

from django.db import models
from extra_validator import FieldValidationMixin


class TestModel(FieldValidationMixin, models.Model):
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    OPTIONAL_TOGGLE_FIELDS = [
        ['fixed_price', 'percentage']  # Optionally validates that only fixed price/percentage are provided when present.
    ]

```

Example

```python
In [1]: from decimal import Decimal

In [2]: from demo.models import TestModel

In [3]: first_obj = TestModel.objects.create(amount=Decimal('2.0'))

In [4]: second_obj = TestModel.objects.create(amount=Decimal('2.0'), fixed_price=Decimal('3.00'))

In [5]: third_obj = TestModel.objects.create(amount=Decimal('2.0'), fixed_price=Decimal('3.00'), percentage=Decimal('10.0'))
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {'percentage': ValidationError([u'Please provide only one of: Fixed price, Percentage'])}

```

### Conditional required fields

```py

from django.db import models
from django.conf import settings
from extra_validator import FieldValidationMixin


class TestModel(FieldValidationMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    CONDITIONAL_REQUIRED_FIELDS = [
        (
            lambda instance: instance.user.is_active, ['amount', 'percentage'],
        ),
    ]

```


Example

```python
In [1]: from decimal import Decimal

in [2]: from django.contrib.auth import get_user_model

In [3]: from demo.models import TestModel

In [4]: user = get_user_model().objects.create(username='test', is_active=True)

In [5]: first_obj = TestModel.objects.create(user=user, amount=Decimal('2.0'))
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {u'percentage': ValidationError([u'Please provide a value for: "percentage"'])}

```

### Conditional required optional fields

```py

from django.db import models
from django.conf import settings
from extra_validator import FieldValidationMixin


class TestModel(FieldValidationMixin, models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

    CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
        (
            lambda instance: instance.user.is_active, ['fixed_price', 'percentage', 'amount'],
        ),
    ]
```

Example

```python
In [1]: from decimal import Decimal

in [2]: from django.contrib.auth import get_user_model

In [3]: from demo.models import TestModel

In [4]: user = get_user_model().objects.create(username='test', is_active=True)

In [5]: first_obj = TestModel.objects.create(user=user)
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {'__all__': ValidationError([u'Please provide a valid value for any of the following fields: Fixed price, Percentage, Amount'])}

In [6]: second_obj = TestModel.objects.create(user=user, amount=Decimal('2'), fixed_price=Decimal('2'))
---------------------------------------------------------------------------
ValueError                   Traceback (most recent call last)
...

ValueError: {'__all__': ValidationError([u'Please provide only one of the following fields: Fixed price, Percentage, Amount'])}
```


Model Attributes
----------------

This is done using model attributes below.

```py
# A list of required fields
REQUIRED_FIELDS = []

#  A list of fields with at most one required.
REQUIRED_TOGGLE_FIELDS = []

# A list of field with at least one required.
REQUIRED_MIN_FIELDS = []

# Optional list of fields with at most one required.
OPTIONAL_TOGGLE_FIELDS = []

# Conditional field required list of tuples the condition a boolean or a callable.
# [(lambda user: user.is_admin, ['first_name', 'last_name'])] : Both 'first_name' or 'last_name'
# If condition is True ensure that all fields are set
CONDITIONAL_REQUIRED_FIELDS = []

# [(lambda user: user.is_admin, ['first_name', 'last_name'])] : Either 'first_name' or 'last_name'
# If condition is True ensure that at most one field is set
CONDITIONAL_REQUIRED_TOGGLE_FIELDS = []

# [(lambda user: user.is_admin, ['first_name', 'last_name'])] : At least 'first_name' or 'last_name' provided or both
# If condition is True ensure that at least one field is set
CONDITIONAL_REQUIRED_MIN_FIELDS = []

# [(lambda user: user.is_admin, ['first_name', 'last_name'])] : Both 'first_name' and 'last_name' isn't provided
# If condition is True ensure none of the fields are provided
CONDITIONAL_REQUIRED_EMPTY_FIELDS = []

```

License
-------

django-extra-field-validation is distributed under the terms of both

  - [MIT License](https://choosealicense.com/licenses/mit)
  - [Apache License, Version 2.0](https://choosealicense.com/licenses/apache-2.0)

at your option.

TODO's
------
  - Support `CONDITIONAL_NON_REQUIRED_TOGGLE_FIELDS`
  - Support `CONDITIONAL_NON_REQUIRED_FIELDS`
  - Move to support class and function based validators that use the instance object this should enable cross field model validation.
