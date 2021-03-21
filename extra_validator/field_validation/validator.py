from __future__ import print_function

import django
from django.core import validators
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models

if django.VERSION <= (3, 0):
    from django.utils.translation import ugettext as _
else:
    from django.utils.translation import gettext as _


def field_to_str(fields):
    return _(
        ", ".join(
            map(lambda fname: fname.replace("_", " ").strip().capitalize(), fields)
        ),
    )


class FieldValidationMixin(object):
    # A list of required fields
    REQUIRED_FIELDS = []
    #  A list of fields with at most one required.
    REQUIRED_TOGGLE_FIELDS = []
    # A list of field with at least one required.
    REQUIRED_MIN_FIELDS = []
    # Optional list of fields with at most one required.
    OPTIONAL_TOGGLE_FIELDS = []

    # Conditional field required list of tuples the condition a boolean or a callable.
    # (lambda o: o.offer_type != Offer.OfferType.OTHER.value, ['offer_detail_id', 'content_type'])
    # If condition is True ensure that all fields are set
    CONDITIONAL_REQUIRED_FIELDS = []
    # If condition is True ensure that at most one field is set
    CONDITIONAL_REQUIRED_TOGGLE_FIELDS = []
    # If condition is True ensure that at least one field is set
    CONDITIONAL_REQUIRED_MIN_FIELDS = []
    # If condition is True ensure none of the fields are provided
    CONDITIONAL_REQUIRED_EMPTY_FIELDS = []

    ERROR_HANDLERS = {"form": ValidationError}

    EMPTY_VALUES = list(validators.EMPTY_VALUES)

    @staticmethod
    def _error_as_dict(field, msg, code="required", error_class=ValidationError):
        return {field: error_class(_(msg), code=code)}

    def _validate_only_one_option(self, selections, found_keys):
        error_dict = {}
        for section in selections:
            provided_fields = []
            for key in found_keys:
                if key in section:
                    provided_fields.append(key)
            if len(set(provided_fields)) > 1:
                msg = "Please provide only one of: {fields}".format(
                    fields=field_to_str(section)
                )
                error_dict.update(
                    self._error_as_dict(provided_fields[-1], msg, code="invalid")
                )
                break
        return error_dict

    def _clean_conditional_toggle_fields(self, exclude=None, context=None):
        if self.CONDITIONAL_REQUIRED_TOGGLE_FIELDS:
            return self._clean_conditional_fields(
                exclude,
                context,
                field_sets=self.CONDITIONAL_REQUIRED_TOGGLE_FIELDS,
                validate_one=True,
            )

    def _clean_conditional_min_fields(self, exclude=None, context=None):
        if self.CONDITIONAL_REQUIRED_MIN_FIELDS:
            return self._clean_conditional_fields(
                exclude,
                context,
                field_sets=self.CONDITIONAL_REQUIRED_MIN_FIELDS,
                at_least_one=True,
            )

    def _clean_conditional_empty_fields(self, exclude=None, context=None):
        if self.CONDITIONAL_REQUIRED_EMPTY_FIELDS:
            return self._clean_conditional_fields(
                exclude,
                context,
                field_sets=self.CONDITIONAL_REQUIRED_EMPTY_FIELDS,
                none_provided=True,
            )

    def _clean_conditional_fields(
        self,
        exclude=None,
        context=None,
        field_sets=(),
        validate_one=False,
        at_least_one=False,
        none_provided=False,
    ):
        error_class = self.ERROR_HANDLERS.get(context, ValueError)
        exclude = exclude or []
        errors = {}
        field_sets = field_sets or self.CONDITIONAL_REQUIRED_FIELDS

        if all([field_sets, isinstance(field_sets, (list, tuple))]):
            try:
                for condition, fields in field_sets:
                    field_names = list(filter(lambda f: f not in exclude, fields))
                    if field_names:
                        is_valid_condition = (
                            condition if isinstance(condition, bool) else False
                        )
                        if callable(condition):
                            is_valid_condition = condition(self)

                        field_value_map = {
                            field_name: getattr(self, field_name)
                            for field_name in field_names
                            if getattr(self, field_name) not in self.EMPTY_VALUES
                        }

                        if is_valid_condition:
                            if not field_value_map and not none_provided:
                                if len(fields) > 1:
                                    msg = (
                                        "Please provide a valid value for the following fields: "
                                        "{fields}"
                                        if not validate_one
                                        else "Please provide a valid value for any of the following fields: "
                                        "{fields}".format(fields=field_to_str(fields))
                                    )
                                    errors.update(
                                        self._error_as_dict(NON_FIELD_ERRORS, msg)
                                    )
                                else:
                                    field = fields[0]
                                    msg = (
                                        'Please provide a value for: "{field}"'.format(
                                            field=field
                                        )
                                    )
                                    errors.update(self._error_as_dict(field, msg))
                                break

                            if field_value_map and none_provided:
                                msg = "Please omit changes to the following fields: {fields}".format(
                                    fields=field_to_str(fields)
                                )
                                errors.update(
                                    self._error_as_dict(NON_FIELD_ERRORS, msg)
                                )
                                break

                            missing_fields = [
                                field_name
                                for field_name in fields
                                if field_name not in field_value_map.keys()
                            ]

                            if (
                                not validate_one
                                and not at_least_one
                                and not none_provided
                            ):
                                for missing_field in missing_fields:
                                    msg = 'Please provide a value for: "{missing_field}"'.format(
                                        missing_field=missing_field
                                    )
                                    errors.update(
                                        self._error_as_dict(missing_field, msg)
                                    )

                            elif validate_one and len(fields) - 1 != len(
                                list(missing_fields)
                            ):
                                msg = "Please provide only one of the following fields: {fields}".format(
                                    fields=field_to_str(fields)
                                )
                                errors.update(
                                    self._error_as_dict(NON_FIELD_ERRORS, msg)
                                )

            except ValueError:
                pass
            else:
                if errors:
                    raise error_class(errors)

    def _clean_required_and_optional_fields(self, exclude=None, context=None):
        """Provide extra validation for fields that are required and single selection fields."""
        exclude = exclude or []
        if any(
            [
                self.REQUIRED_TOGGLE_FIELDS,
                self.REQUIRED_MIN_FIELDS,
                self.REQUIRED_FIELDS,
                self.OPTIONAL_TOGGLE_FIELDS,
            ]
        ):
            error_class = self.ERROR_HANDLERS.get(context, ValueError)
            found = []
            errors = {}
            optional = []

            for f in self._meta.fields:
                if f.name not in exclude:
                    raw_value = getattr(self, f.attname)
                    if f.name in self.REQUIRED_FIELDS:
                        if raw_value in f.empty_values and not f.has_default():
                            msg = 'Please provide a value for: "{field_name}".'.format(
                                field_name=f.name
                            )
                            errors.update(self._error_as_dict(f.name, msg))

                    for required_min_field in self.REQUIRED_MIN_FIELDS:
                        # Multiple selection of at least one required.
                        if f.name in required_min_field:
                            if raw_value not in f.empty_values:
                                found.append({f.name: raw_value})
                            elif raw_value in f.empty_values and f.has_default():
                                if (
                                    isinstance(f, models.CharField)
                                    and f.get_default() not in f.empty_values
                                ):
                                    found.append({f.name: f.get_default()})

                    for required_toggle_field in self.REQUIRED_TOGGLE_FIELDS:
                        # Single selection of at most one required.
                        if f.name in required_toggle_field:
                            if raw_value not in f.empty_values:
                                found.append({f.name: raw_value})
                            elif raw_value in f.empty_values and f.has_default():
                                if (
                                    isinstance(f, models.CharField)
                                    and f.get_default() not in f.empty_values
                                ):
                                    found.append({f.name: f.get_default()})

                    for optional_toggle_field in self.OPTIONAL_TOGGLE_FIELDS:
                        if (
                            f.name in optional_toggle_field
                            and raw_value not in f.empty_values
                        ):
                            optional.append({f.name: raw_value})

            if self.REQUIRED_MIN_FIELDS:
                if not found:
                    fields_str = "\n, ".join(
                        [field_to_str(fields) for fields in self.REQUIRED_MIN_FIELDS]
                    )
                    fields_str = (
                        "\n {fields}".format(fields=fields_str)
                        if len(self.REQUIRED_MIN_FIELDS) > 1
                        else fields_str
                    )
                    msg = "Please provide a valid value for any of the following fields: {fields}".format(
                        fields=fields_str
                    )
                    errors.update(self._error_as_dict(NON_FIELD_ERRORS, msg))

            if self.REQUIRED_TOGGLE_FIELDS:
                if not found:
                    fields_str = "\n, ".join(
                        [field_to_str(fields) for fields in self.REQUIRED_TOGGLE_FIELDS]
                    )
                    fields_str = (
                        "\n {fields}".format(fields=fields_str)
                        if len(self.REQUIRED_TOGGLE_FIELDS) > 1
                        else fields_str
                    )
                    msg = "Please provide a valid value for any of the following fields: {fields}".format(
                        fields=fields_str
                    )
                    errors.update(self._error_as_dict(NON_FIELD_ERRORS, msg))
                else:
                    found_keys = [k for item in found for k in item.keys()]
                    errors.update(
                        self._validate_only_one_option(
                            self.REQUIRED_TOGGLE_FIELDS, found_keys
                        ),
                    )

            if self.OPTIONAL_TOGGLE_FIELDS:
                if optional:
                    optional_keys = [k for item in optional for k in item.keys()]
                    errors.update(
                        self._validate_only_one_option(
                            self.OPTIONAL_TOGGLE_FIELDS, optional_keys
                        ),
                    )

            if errors:
                raise error_class(errors)

    def clean_fields(self, exclude=None):
        self._clean_conditional_toggle_fields(exclude=exclude, context="form")
        self._clean_conditional_min_fields(exclude=exclude, context="form")
        self._clean_conditional_empty_fields(exclude=exclude, context="form")
        self._clean_conditional_fields(exclude=exclude, context="form")
        self._clean_required_and_optional_fields(exclude=exclude, context="form")
        return super(FieldValidationMixin, self).clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        self._clean_conditional_toggle_fields()
        self._clean_conditional_min_fields()
        self._clean_conditional_empty_fields()
        self._clean_conditional_fields()
        self._clean_required_and_optional_fields()
        return super(FieldValidationMixin, self).save(*args, **kwargs)
