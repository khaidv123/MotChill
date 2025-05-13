#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MotChill.settings')

    '''==> This function is the entry point for the script. It sets the DJANGO_SETTINGS_MODULE environment
      variable to point to your Django project’s settings. In this case, it's set to 'MotChill.settings',
        which is where Django will look for the configuration settings.'''

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

    '''==> The script tries to import execute_from_command_line from django.core.management. 
    This function is responsible for executing commands passed to manage.py 
    (like runserver, migrate, createsuperuser, etc.).'''


if __name__ == '__main__':
    main()
