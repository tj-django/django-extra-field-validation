#!/usr/bin/env python
import os
from future.utils import raise_from
import sys

if __name__ == "__main__":
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "django_extra_field_validation.settings"
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise_from(
            ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            ),
            exc,
        )
    execute_from_command_line(sys.argv)
