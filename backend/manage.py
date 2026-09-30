#!/usr/bin/env python
"""Point d'entree des commandes Django."""
import os
import sys


def main():
    """Execute les commandes d'administration avec la configuration de dev."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
