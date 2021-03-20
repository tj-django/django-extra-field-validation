# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django
from six import python_2_unicode_compatible

from django.contrib.auth import get_user_model
from django.db import models

from extra_validator import FieldValidationMixin

if django.VERSION <= (3, 0):
    from django.utils.translation import ugettext_noop as _
else:
    from django.utils.translation import gettext_noop as _

UserModel = get_user_model()


@python_2_unicode_compatible
class TestModel(FieldValidationMixin, models.Model):
    """Ensure that at least one of the following fields are provided."""

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fixed_price = models.DecimalField(
        max_digits=7, decimal_places=2, null=True, blank=True
    )
    percentage = models.DecimalField(
        max_digits=3, decimal_places=0, null=True, blank=True
    )

    def __str__(self):
        return _(
            "{0}: (#{1}, {2}%, ${3})".format(
                self.__class__.__name__, self.amount, self.percentage, self.fixed_price
            )
        )
