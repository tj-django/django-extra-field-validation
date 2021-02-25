import django
from django.core import validators
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.db import models

if django.VERSION <= (3, 0):
    from django.utils.translation import ugettext as _
else:
    from django.utils.translation import gettext as _


class ModelFieldRequiredMixin(object):
    #  A list of iterable with a field required from each section.
    REQUIRED_TOGGLE_FIELDS = []
    #  # A single list of required fields
    REQUIRED_FIELDS = []
    # Optional toggle fields.
    OPTIONAL_TOGGLE_FIELDS = []
    # Conditional field required list of tuples the condition a boolean or a callable.
    # (lambda o: o.offer_type != Offer.OfferType.OTHER.value, ['offer_detail_id', 'content_type'])
    CONDITIONAL_REQUIRED_FIELDS = []
    CONDITIONAL_REQUIRED_TOGGLE_FIELDS = []

    ERROR_HANDLERS = {"form": ValidationError}

    _EMPTY_VALUES = list(validators.EMPTY_VALUES)

    @classmethod
    def field_to_str(cls, fields):
        return _(
            ", ".join(
                map(lambda fname: fname.replace("_", " ").strip().capitalize(), fields)
            ),
        )

    def _validate_only_one_option(self, selections, found_keys):
        error_dict = {}
        for section in selections:
            provided_fields = []
            for key in found_keys:
                if key in section:
                    provided_fields.append(key)
            if len(set(provided_fields)) > 1:
                fields = self.field_to_str(section)
                msg = "Please provide only one of: {fields}".format(fields=fields)
                error_dict.update(
                    self._add_error(provided_fields[-1], msg, code="invalid")
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

    def _clean_conditional_fields(
        self, exclude=None, context=None, field_sets=(), validate_one=False
    ):
        error_class = self.ERROR_HANDLERS.get(context, ValueError)
        exclude = exclude or []
        errors = {}
        field_sets = field_sets or self.CONDITIONAL_REQUIRED_FIELDS

        if all([field_sets, isinstance(field_sets, (list, tuple))]):
            try:
                for condition, fields in field_sets:
                    fields = list(filter(lambda f: f not in exclude, fields))
                    if fields:
                        is_valid_condition = (
                            condition if isinstance(condition, bool) else False
                        )
                        if callable(condition):
                            is_valid_condition = condition(self)
                        field_value_dict = dict(
                            [
                                (fname, getattr(self, fname))
                                for fname in fields
                                if getattr(self, fname) not in self._EMPTY_VALUES
                            ]
                        )
                        missing_fields = filter(
                            lambda fn: fn not in field_value_dict.keys(), fields
                        )

                        if is_valid_condition:
                            field_names = self.field_to_str(fields)
                            if not field_value_dict:
                                if len(fields) > 1:
                                    msg = (
                                        "Please provide a valid value for the following fields:"
                                        " {0}".format(field_names)
                                        if not validate_one
                                        else "Please provide a valid value for any of the following"
                                        " fields: {0}".format(field_names)
                                    )
                                    errors.update(
                                        self._add_error(NON_FIELD_ERRORS, msg)
                                    )
                                else:
                                    msg = 'Please provide a value for: "{0}"'.format(
                                        fields[-1]
                                    )
                                    errors.update(self._add_error(fields[-1], msg))
                                break
                            if not validate_one:
                                for missing_field in missing_fields:
                                    msg = 'Please provide a value for: "{missing_field}"'.format(
                                        missing_field=missing_field
                                    )
                                    errors.update(self._add_error(missing_field, msg))
                            elif validate_one and len(fields) - 1 != len(
                                list(missing_fields)
                            ):
                                msg = "Please provide only one of the following fields: {0}".format(
                                    field_names
                                )
                                errors.update(self._add_error(NON_FIELD_ERRORS, msg))
            except ValueError:
                pass
            else:
                if errors:
                    raise error_class(errors)

    @staticmethod
    def _add_error(field, msg, code="required", error_class=ValidationError):
        errors = {field: error_class(_(msg), code=code)}
        return errors

    def _clean_required_and_optional_fields(self, exclude=None, context=None):
        """Provide extra validation for fields that are required and single selection fields."""
        exclude = exclude or []
        if any(
            [
                self.REQUIRED_TOGGLE_FIELDS,
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
                            msg = 'Please provide a value for: "{0}".'.format(f.name)
                            errors.update(self._add_error(f.name, msg))

                    for required_toggle_field in self.REQUIRED_TOGGLE_FIELDS:
                        # Single selection of at least one required.
                        if f.name in required_toggle_field:
                            if raw_value not in f.empty_values:
                                found.append({f.name: raw_value})
                            elif raw_value in f.empty_values and f.has_default():
                                if all(
                                    [
                                        isinstance(f, models.CharField),
                                        f.get_default() not in f.empty_values,
                                    ]
                                ):
                                    found.append({f.name: f.get_default()})

                    for optional_toggle_field in self.OPTIONAL_TOGGLE_FIELDS:
                        if (
                            f.name in optional_toggle_field
                            and raw_value not in f.empty_values
                        ):
                            optional.append({f.name: raw_value})

            if self.REQUIRED_TOGGLE_FIELDS:
                if not found:
                    fields_str = "\n, ".join(
                        [
                            self.field_to_str(fields)
                            for fields in self.REQUIRED_TOGGLE_FIELDS
                        ]
                    )
                    fields_str = (
                        "\n {0}".format(fields_str)
                        if len(self.REQUIRED_TOGGLE_FIELDS) > 1
                        else fields_str
                    )
                    msg = "Please provide a valid value for any of the following fields: {fields_str}".format(
                        fields_str=fields_str
                    )
                    errors.update(self._add_error(NON_FIELD_ERRORS, msg))
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
        self._clean_conditional_fields(exclude=exclude, context="form")
        self._clean_required_and_optional_fields(exclude=exclude, context="form")
        return super(ModelFieldRequiredMixin, self).clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        self._clean_conditional_toggle_fields()
        self._clean_conditional_fields()
        self._clean_required_and_optional_fields()
        return super(ModelFieldRequiredMixin, self).save(*args, **kwargs)
