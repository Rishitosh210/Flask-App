#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
	if sys.argv[1]=="migrate":
		raise "Dont use migrate!! Brother"
	os.environ.setdefault("DJANGO_SETTINGS_MODULE", "audtech_project.settings")
  

	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)
