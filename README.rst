.. image:: https://badge.fury.io/py/django-dynamic-model-validation.svg
    :target: https://badge.fury.io/py/django-dynamic-model-validation
.. image:: https://travis-ci.org/jackton1/django-dynamic-model-validation.svg?branch=master
    :target: https://travis-ci.org/jackton1/django-dynamic-model-validation
.. image:: https://api.codacy.com/project/badge/Coverage/33797e94524e4277b476c051618ad495    
    :target: https://www.codacy.com/app/jackton1/django-dynamic-model-validation?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jackton1/django-dynamic-model-validation&amp;utm_campaign=Badge_Coverage
.. image:: https://api.codacy.com/project/badge/Grade/33797e94524e4277b476c051618ad495
    :target: https://www.codacy.com/app/jackton1/django-dynamic-model-validation?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jackton1/django-dynamic-model-validation&amp;utm_campaign=Badge_Grade

Extra model validation.

django-dynamic-model-validation
===============================



.. contents:: **Table of Contents**
    :backlinks: none

Introduction
------------
This package aims to provide tools needed to define custom field validation logic once which can be used independently or with
django forms, test cases, API implementation or any model operation that requires saving data to the
database.

This can also be extended by defining table check constraints if needed but currently validation
will only be handled at the model level.


Installation
------------

django-dynamic-model-validation is distributed on `PyPI <https://pypi.org>`_ as a universal
wheel and is available on Linux/macOS and Windows and supports
Python 2.7/3.5+ and PyPy.

.. code-block:: bash

    $ pip install django-dynamic-model-validation

.. code-block:: python

   INSTALLED_APPS = [
       ...
       'dynamic_validator',
   ]

Usage
-----
This provides model level validation which includes conditional validation, cross field validation,
required field validation etc.


This is done using model attributes below.

.. code-block:: python

    #  Using a list/iterable list: [['a', 'b'], ['c', 'd']] which validates that a field required from each section.
    REQUIRED_TOGGLE_FIELDS = []

    # Using a list/iterable validated that all required fields are provided.
    REQUIRED_FIELDS = []

    # Optional toggle fields list: [['a', 'b']] which runs the validation only when any of the fields are present.
    OPTIONAL_TOGGLE_FIELDS = []

    # Conditional field validation using a list of tuples the condition a boolean or a callable and list/iterable of fields.
    # [(condition, [fields]), (condition, fields)]

    # Using a callable [(lambda instance: instance.is_admin, ['a', 'd'])]
    # Using a boolean [(True, ['b', 'c']), (True, ['d', f])] 
    # (Note: This can also be handled using REQUIRED_FIELDS/REQUIRED_TOGGLE_FIELDS)

    # Validates that all fields are present if the condition is True
    CONDITIONAL_REQUIRED_FIELDS = []
    # Validated at least one not both fields are provided if the condition is True.
    CONDITIONAL_REQUIRED_TOGGLE_FIELDS = []


[Validates] That one of the listed fields are be provided.
**********************************************************

.. code-block:: python

    from django.db import models
    from dynamic_validator import ModelFieldRequiredMixin


    class TestModel(ModelFieldRequiredMixin, models.Model):
        amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
        percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

        REQUIRED_TOGGLE_FIELDS = [
            ['amount', 'fixed_price', 'percentage'],
        ]

.. code-block:: bash

    $ python manage.py shell
    ...
    >>> from decimal import Decimal
    >>> from demo.models import TestModel
    >>> TestModel.objects.create(amount=Decimal('2.50'), fixed_price=Decimal('3.00'))
    ...
    ValueError: {'fixed_price': ValidationError([u'Please provide only one of: Amount, Fixed price, Percentage'])}

[Validates] That a field without a default is required.
*******************************************************

.. code-block:: python

    from django.db import models
    from dynamic_validator import ModelFieldRequiredMixin


    class TestModel(ModelFieldRequiredMixin, models.Model):
        amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
        percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

        REQUIRED_FIELDS = ['amount']  # Always requires an amount to create the instance.

.. code-block:: bash

    $ python manage.py shell
    ...
    >>> from decimal import Decimal
    >>> from demo.models import TestModel
    >>> TestModel.objects.create(fixed_price=Decimal('3.00'))
    ...
    ValueError: {'amount': ValidationError([u'Please provide a value for: "amount".'])}


[Validates] That optional fields should only have one value if provided.
************************************************************************

.. code-block:: python

    from django.db import models
    from dynamic_validator import ModelFieldRequiredMixin


    class TestModel(ModelFieldRequiredMixin, models.Model):
        amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
        percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

        OPTIONAL_TOGGLE_FIELDS = [
            ['fixed_price', 'percentage']  # Optionally validates that only fixed price/percentage are provided.
        ]

.. code-block:: bash

    $ python manage.py shell
    ...
    >>> from decimal import Decimal
    >>> from demo.models import TestModel
    >>> first_obj = TestModel.objects.create(amount=Decimal('2.0'))
    >>> second_obj = TestModel.objects.create(amount=Decimal('2.0'), fixed_price=Decimal('3.00'))
    >>> third_obj = TestModel.objects.create(amount=Decimal('2.0'), fixed_price=Decimal('3.00'), percentage=Decimal('10.0'))
    ...
    ValueError: {'percentage': ValidationError([u'Please provide only one of: Fixed price, Percentage'])}


[Validates] That when a user is active (ie. instance.user.is_active) both fields should be provided.
****************************************************************************************************

.. code-block:: python

    from django.db import models
    from django.conf import settings
    from dynamic_validator import ModelFieldRequiredMixin


    class TestModel(ModelFieldRequiredMixin, models.Model):
        user = models.ForeignKey(settings.AUTH_USER_MODEL)

        amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
        percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

        CONDITIONAL_REQUIRED_FIELDS = [
            (
                lambda instance: instance.user.is_active, ['amount', 'percentage'],
            ),
        ]

.. code-block:: bash

    $ python manage.py shell
    ...
    >>> from decimal import Decimal
    >>> from django.contrib.auth import get_user_model
    >>> from demo.models import TestModel
    >>> user = get_user_model().objects.create(username='test', is_active=True)
    >>> first_obj = TestModel.objects.create(user=user, amount=Decimal('2.0'))
    ...
    ValueError: {u'percentage': ValidationError([u'Please provide a value for: "percentage"'])}

[Validates] That when a user is active (ie. instance.user.is_active) any of the fields should be provided (i.e only one).
*************************************************************************************************************************

.. code-block:: python

    from django.db import models
    from django.conf import settings
    from dynamic_validator import ModelFieldRequiredMixin


    class TestModel(ModelFieldRequiredMixin, models.Model):
        user = models.ForeignKey(settings.AUTH_USER_MODEL)

        amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
        fixed_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
        percentage = models.DecimalField(max_digits=3, decimal_places=0, null=True, blank=True)

        CONDITIONAL_REQUIRED_TOGGLE_FIELDS = [
            (
                lambda instance: instance.user.is_active, ['fixed_price', 'percentage', 'amount'],
            ),
        ]

.. code-block:: bash

    $ python manage.py shell
    ...
    >>> from decimal import Decimal
    >>> from django.contrib.auth import get_user_model
    >>> from demo.models import TestModel
    >>> user = get_user_model().objects.create(username='test', is_active=True)
    >>> first_obj = TestModel.objects.create(user=user)
    ...
    ValueError: {'__all__': ValidationError([u'Please provide a valid value for any of the following fields: Fixed price, Percentage, Amount'])}
    ...
    >>>first_obj = TestModel.objects.create(user=user, amount=Decimal('2'), fixed_price=Decimal('2'))
    ...
    ValueError: {'__all__': ValidationError([u'Please provide only one of the following fields: Fixed price, Percentage, Amount'])}
    ...


License
-------

django-dynamic-model-validation is distributed under the terms of both

- `MIT License <https://choosealicense.com/licenses/mit>`_
- `Apache License, Version 2.0 <https://choosealicense.com/licenses/apache-2.0>`_

at your option.
