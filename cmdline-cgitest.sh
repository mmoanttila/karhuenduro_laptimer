#!/bin/bash
HTTP_USER_AGENT=cmdline QUERY_STRING="${1:-date=20190910}" ./parse.py
