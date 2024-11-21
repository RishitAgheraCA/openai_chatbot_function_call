#!/usr/bin/env python
import os
import sys
from pathlib import Path
from config.settings.conf import app_config

if __name__ == "__main__":
    DJANGO_SETTINGS_MODULE = app_config.DJANGO_SETTINGS_MODULE
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        try:
            import django  # noqa
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )

        raise

    # This allows easy placement of apps within the interior
    # src directory.
    current_path = Path(__file__).parent.resolve()
    sys.path.append(str(current_path / "src"))

    execute_from_command_line(sys.argv)
